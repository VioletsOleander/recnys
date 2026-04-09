import logging
from pathlib import Path
from typing import overload

from .model import BranchNode, RootNode, LeafNode
from .utils.traversal import walk_tree

logger = logging.getLogger(__name__)

# add creation node after execution
# delete deletion node after execution
class TreeExecutor:
    executed: list[Path]
    dry_run: bool

    def __init__(self, *, dry_run: bool) -> None:
        self.executed = []
        self.dry_run = dry_run

    def execute(self, root: RootNode) -> RootNode:
        self._execute_nonleaf(root)

        return root

    @overload
    def _execute_nonleaf(self, node: RootNode) -> RootNode: ...
    @overload
    def _execute_nonleaf(self, node: BranchNode) -> BranchNode: ...

    def _execute_nonleaf(self, node: RootNode | BranchNode) -> RootNode | BranchNode:
        # EAFP style has less syscalls than LBYL style
        try:
            node.dst.mkdir()
        except FileExistsError:
            self.executed.append(node.dst)
            return node
        else:
            self.executed.append(node.dst)
            return node

    def _execute_leaf(self, node: LeafNode) -> LeafNode:
