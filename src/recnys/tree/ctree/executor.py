"""Provide `CTreeExecutor`."""

import logging
from typing import TYPE_CHECKING

from jinja2 import Environment

from recnys.tree.model import BranchNode, CLeafOp, CTree, LeafNode, Node
from recnys.tree.utils.walker import Callbacks, VisitOrder, walk_tree

if TYPE_CHECKING:
    from pathlib import Path

    from recnys.linear.model import ScannedVariables

__all__ = ["CTreeExecutor"]

logger = logging.getLogger(__name__)


class CTreeExecutor:
    """CTreeExecutor executes a creation tree.

    Attributes:
        tree (CTree): The creation tree instance constructed during the execution.
        num_executed_ops (int): The number of operations executed during the execution.
        dry_run (bool): Whether to perform a dry run of the execution.
            If True, the execution will only log the operations without actually performing them.
    """

    tree: CTree
    num_executed_ops: int
    dry_run: bool
    _renderer: _Renderer | None

    def __init__(self, variables: ScannedVariables | None, *, dry_run: bool) -> None:
        """Initialize the CTreeExecutor.

        Args:
            variables (ScannedVariables | None): The variables to be used for rendering templates.
            dry_run (bool): Whether to perform a dry run of the execution.
        """
        self.dry_run = dry_run
        self.num_executed_ops = 0
        self._renderer = _Renderer(variables) if variables is not None else None

    def execute(self, ctree: CTree) -> CTree:
        """Execute the given ctree.

        Return a new ctree with the non-executed nodes detached from the tree. If all nodes are executed
        successfully, the returned ctree will be the same as the given ctree.

        Args:
            ctree (RootNode): The root node of the creation tree to be executed.

        Returns:
            CTree: The creation tree with the non-executed nodes detached from the tree.
        """
        logger.debug("Executing creation tree.")

        self.tree = CTree(root=BranchNode(dst=ctree.root.dst))
        parents: dict[Path, BranchNode] = {self.tree.root.dst: self.tree.root}
        ops = self.tree.ops

        def attach_node(node: Node) -> None:
            parent = parents[node.dst.parent]
            parent.children[node.dst] = node

            if isinstance(node, BranchNode):
                parents[node.dst] = node

        def execute_branch(node: BranchNode) -> None:
            """Execute creation op (create) on branch node (dir).

            Attach the executed node after execution.
            """
            self._mkdir(node.dst)
            branch = BranchNode(dst=node.dst)
            return attach_node(branch)

        def execute_leaf(node: LeafNode) -> None:
            """Execute creation op (copy/render/link) on leaf node (file or dir).

            Attach the executed node after execution.
            """
            op = ctree.ops[node.dst]

            match op:
                case CLeafOp.COPY:
                    self._copy(node.src, node.dst)
                case CLeafOp.RENDER:
                    self._render(node.src, node.dst)
                case CLeafOp.LINK:
                    self._link(node.src, node.dst)

            ops[node.dst] = op
            leaf = LeafNode(src=node.src, dst=node.dst)
            return attach_node(leaf)

        callbacks = Callbacks(branch=execute_branch, leaf=execute_leaf)
        walk_tree(ctree, callbacks=callbacks, order=VisitOrder.PRE)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Executed creation tree: %s", self.tree.model_dump_json(indent=2))

        return self.tree

    def _mkdir(self, dst: Path) -> None:
        if dst.exists():
            if not dst.is_dir():
                raise FileExistsError(
                    f"Path {dst} is occupied, failed to create directory there.\n"
                    "Hint: Please remove the file or symbolic link at the path."
                )

            return logger.debug("Directory %s already exists, skip creation.", dst)

        self.num_executed_ops += 1

        if self.dry_run:
            verb = "Create"
        else:
            dst.mkdir()
            verb = "Created"

        return logger.info("%s directory %s", verb, dst)

    def _skip_write(self, dst: Path, content: str) -> bool:
        if dst.exists():
            if not dst.is_file():
                raise FileExistsError(
                    f"Path {dst} is occupied, failed to write file there.\n"
                    "Hint: Please remove the directory or symbolic link at the path."
                )

            if dst.read_text(encoding="utf-8") == content:
                logger.debug("File %s already exists with the same content, skip writing.", dst)
                return True

        return False

    def _copy(self, src: Path, dst: Path) -> None:
        content = src.read_text(encoding="utf-8")

        if self._skip_write(dst, content):
            return None

        self.num_executed_ops += 1

        if self.dry_run:
            verb = "Copy"
        else:
            _atomic_write(dst, content)
            verb = "Copied"

        return logger.info("%s %s to %s.", verb, src, dst)

    def _render(self, src: Path, dst: Path) -> None:
        if self._renderer is None:
            raise RuntimeError("Renderer is not initialized. Variables are required for rendering.")

        template_content = src.read_text(encoding="utf-8")
        content = self._renderer.render(template_content)

        if self._skip_write(dst, content):
            return None

        self.num_executed_ops += 1

        if self.dry_run:
            verb = "Render"
        else:
            _atomic_write(dst, content)
            verb = "Rendered"

        return logger.info("%s %s to %s.", verb, src, dst)

    def _link(self, src: Path, dst: Path) -> None:
        if dst.exists(follow_symlinks=False):
            if not dst.is_symlink():
                raise FileExistsError(
                    f"Path {dst} is occupied, failed to create symbolic link there.\n"
                    "Hint: Please remove the file or directory at the path."
                )

            if dst.resolve() == src.resolve():
                return logger.debug(
                    "Link %s already exists with the same target, skip linking.", dst
                )

        self.num_executed_ops += 1

        if self.dry_run:
            verb = "Link"
        else:
            dst.unlink(missing_ok=True)
            dst.symlink_to(src)
            verb = "Linked"

        return logger.info("%s %s to %s.", verb, src, dst)


def _atomic_write(f: Path, content: str) -> None:
    """Atomically write content to f."""
    try:
        tmp_f = f.with_suffix(f"{f.suffix}.recnys.tmp")
        tmp_f.write_text(content, encoding="utf-8")
        tmp_f.replace(f)
    finally:
        tmp_f.unlink(missing_ok=True)


class _Renderer:
    """Renderer render jinja templates."""

    _environment: Environment
    _variables: ScannedVariables

    def __init__(self, variables: ScannedVariables) -> None:
        self._variables = variables
        self._environment = Environment(keep_trailing_newline=True, autoescape=False)  # noqa: S701

    def render(self, template_content: str) -> str:
        """Render `template_content` and return the result."""
        template = self._environment.from_string(template_content)
        return template.render(self._variables.root)
