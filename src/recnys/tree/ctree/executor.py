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
        dry_run (bool): Whether to perform a dry run of the execution.
            If True, the execution will only log the operations without actually performing them.
    """

    tree: CTree
    dry_run: bool
    _renderer: _Renderer | None

    def __init__(self, variables: ScannedVariables | None, *, dry_run: bool) -> None:
        """Initialize the CTreeExecutor.

        Args:
            variables (ScannedVariables | None): The variables to be used for rendering templates.
            dry_run (bool): Whether to perform a dry run of the execution.
        """
        self.dry_run = dry_run
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

        logger.debug("Executed creation tree.")
        return self.tree

    def _mkdir(self, dst: Path) -> None:
        if self.dry_run and not dst.exists():
            return logger.info("Create directory %s", dst)

        try:
            dst.mkdir()
        except FileExistsError:
            return logger.debug("Directory %s already exists, skip creation.", dst)
        else:
            return logger.info("Created directory %s", dst)

    def _copy(self, src: Path, dst: Path) -> None:
        content = src.read_text(encoding="utf-8")
        if dst.exists() and dst.read_text(encoding="utf-8") == content:
            return logger.debug("File %s already exists with the same content, skip copying.", dst)

        if self.dry_run:
            return logger.info("Copy %s to %s.", src, dst)

        _atomic_write(dst, content)
        return logger.info("Copied %s to %s.", src, dst)

    def _render(self, src: Path, dst: Path) -> None:
        if self._renderer is None:
            raise RuntimeError("Renderer is not initialized. Variables are required for rendering.")

        template_content = src.read_text(encoding="utf-8")
        content = self._renderer.render(template_content)

        if dst.exists() and dst.read_text(encoding="utf-8") == content:
            return logger.debug(
                "File %s already exists with the same content, skip rendering.", dst
            )

        if self.dry_run:
            return logger.info("Render %s to %s.", src, dst)

        _atomic_write(dst, content)
        return logger.info("Rendered %s to %s.", src, dst)

    def _link(self, src: Path, dst: Path) -> None:
        if dst.exists(follow_symlinks=False) and dst.resolve() == src.resolve():
            return logger.debug("Link %s already exists with the same target, skip linking.", dst)

        if self.dry_run:
            return logger.info("Link %s to %s.", src, dst)

        dst.symlink_to(src)
        return logger.info("Linked %s to %s.", src, dst)


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
        return template.render(self._variables)
