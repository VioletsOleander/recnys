"""Provide `CTreeExecutor`."""

import logging
import os
import tempfile
from typing import TYPE_CHECKING, overload

from jinja2 import Environment

from recnys.backend.model import BranchNode, LeafNode, Operation, RootNode
from recnys.backend.utils.collector import collect_nodes
from recnys.backend.utils.traversal import Callbacks, Order, walk_tree
from recnys.frontend.model import ScannedVariables

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)

__all__ = ["CTreeExecutor"]


class CTreeExecutor:
    """CTreeExecutor executes a creation tree.

    Attributes:
        ctree (RootNode): The root node of the creation tree after execution.
        dry_run (bool): Whether to perform a dry run of the execution.
            If True, the execution will only log the operations without actually performing them.
    """

    ctree: RootNode
    dry_run: bool
    _renderer: _Renderer
    _parent_nodes: dict[Path, RootNode | BranchNode]

    def __init__(self, variables: ScannedVariables, *, dry_run: bool) -> None:
        """Initialize the DTreeExecutor.

        Args:
            variables (ScannedVariables): The variables to be used for rendering templates.
            dry_run (bool): Whether to perform a dry run of the execution.
        """
        self.dry_run = dry_run
        self._renderer = _Renderer(variables)

    def execute(self, ctree: RootNode) -> RootNode:
        """Execute the given ctree.

        Return a new ctree with the non-executed nodes detached from the tree. If all nodes are executed
        successfully, the returned ctree will be the same as the given ctree.

        Args:
            ctree (RootNode): The root node of the creation tree to be executed.

        Returns:
            RootNode: The root node of the creation tree with the non-executed nodes detached from the tree.
        """
        self.ctree = RootNode(dst=ctree.dst)
        self._parent_nodes = {self.ctree.dst: self.ctree}

        callbacks = Callbacks(root=None, branch=self._execute_branch, leaf=self._execute_leaf)
        walk_tree(ctree, callbacks=callbacks, order=Order.POST, update=False)
        return ctree

    def _execute_branch(self, node: BranchNode) -> BranchNode:
        """Execute creation op (create) on branch node (dir).

        Attach the executed node to self.ctree and return it.
        """
        if node.op != Operation.CREATE:
            raise RuntimeError(
                f"Invalid ctree, expect operation for branch node to be {Operation.CREATE}, "
                f"but encounter {node.op}"
            )

        if self.dry_run:
            logger.info("Create %s, no effect if it already exists", node.dst)

        try:
            node.dst.mkdir()
            logger.info("Created %s", node.dst)
        except FileExistsError:
            return self._attach_node(node)
        else:
            return self._attach_node(node)

    def _execute_leaf(self, node: LeafNode) -> LeafNode:
        """Execute creation op (copy/render/link) on leaf node (file or dir)."""
        valid_ops = (Operation.COPY, Operation.LINK, Operation.RENDER)
        if node.op not in valid_ops:
            raise RuntimeError(
                f"Invalid ctree, expect operation for leaf node to be one of {valid_ops}, "
                f"but encounter {node.op}"
            )

        if node.op == Operation.NOP:
            return self._attach_node(node)

        if self.dry_run:
            logger.info("Unlink %s, no effect if it does not exist.", node.dst)
            return self._attach_node(node)

        node.dst.unlink(missing_ok=True)
        logger.info("Unlinked %s", node.dst)

        return self._attach_node(node)

    @overload
    def _attach_node(self, node: BranchNode) -> BranchNode: ...

    @overload
    def _attach_node(self, node: LeafNode) -> LeafNode: ...

    def _attach_node(self, node: BranchNode | LeafNode) -> BranchNode | LeafNode:
        parent = self._parent_nodes[node.dst.parent]
        parent.children[node.dst] = node

        if isinstance(node, BranchNode):
            self._parent_nodes[node.dst] = node

        return node


def _atomic_write(f: Path, content: str) -> None:
    """Atomically write content to f."""
    try:
        tmp_f = f.with_suffix(f"{f.suffix}.recnys.tmp")
        tmp_f.write_text(content, encoding="utf-8")
        tmp_f.replace(f)
    except Exception:
        tmp_f.unlink(missing_ok=True)
        raise


class _Renderer:
    """Renderer render jinja templates."""

    _environment: Environment
    _variables: ScannedVariables

    def __init__(self, variables: ScannedVariables) -> None:
        self._variables = variables
        self._environment = Environment(keep_trailing_newline=True, autoescape=False)  # noqa: S701

    def render(self, template_content: str) -> str:
        """Return rendered content."""
        template = self._environment.from_string(template_content)
        return template.render(self._variables)
