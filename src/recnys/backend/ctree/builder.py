"""Provide `CTreeBuilder`."""

from pathlib import Path
from typing import TYPE_CHECKING

from recnys.backend.model import BranchNode, CLeafOp, CTree, LeafNode
from recnys.frontend.model import EntryValue, Policy, ScannedConfig
from recnys.utils.platform import Platform

from .utils import handle_fnf

if TYPE_CHECKING:
    from recnys.utils.paths import Paths

__all__ = ["CTreeBuilder"]


class CTreeBuilder:
    """CTreeBuilder transforms the scanned configuration into a creation tree.

    Because what recnys manipulates is the filesystem, therefore tree structure is very natural for acting as
    an intermediate representation.

    The main provided method is `build`.
    """

    _tree: CTree
    _paths: Paths
    _platform: Platform

    def __init__(self, paths: Paths, platform: Platform) -> None:
        """Initialize the CTreeBuilder.

        Args:
            paths (Paths): The Paths instance containing relevant paths.
            platform (Platform): The current platform.
        """
        self._paths = paths
        self._platform = platform

    def build(self, scanned_config: ScannedConfig) -> CTree:
        """Construct a creation tree from the scanned configuration.

        During the parsing process, features from features/deconflict are satisfied.

        Args:
            scanned_config (ScannedConfig): The scanned configuration to be parsed.

        Returns:
            CTree: The constructed creation tree.
        """
        self._tree = CTree(root=BranchNode(dst=self._paths.home))

        for key, val in scanned_config.root.items():
            dst = self._get_dst(key, val)
            if dst is None:
                continue

            src = self._paths.repo_dir / key
            op = self._get_op(key, val)
            self._make_nodes(src=src, dst=dst, op=op)

        return self._tree

    def _make_nodes(self, src: Path, dst: Path, op: CLeafOp) -> None:
        """Make leaf node and branch nodes on its way to the root node.

        If conflict leaf nodes are met during making branch nodes, they will be recursively branchified.
        If conflict leaf/branch node is met during making leaf node, it will be replaced, and its subtree (if
        exists) is thus dropped.

        All features specified in features/deconflict are satisfied by this implementation.

        Args:
            src (Path): The source path of the leaf node to be made.
            dst (Path): The destination path of the leaf node to be made.
            op (CLeafOp): The operation of the leaf node to be made.
        """
        root = self._tree.root
        ops = self._tree.ops

        parent = root
        num_exclude = len(root.dst.parents) + 1  # exclude home and its parents

        for branch_dst in reversed(dst.parents[:-num_exclude]):
            if branch_dst in parent.children:
                node = parent.children[branch_dst]
                branch = self._branchify_leaf(node, src) if isinstance(node, LeafNode) else node
            else:
                branch = BranchNode(dst=branch_dst)

            parent.children[branch_dst] = branch
            parent = branch

        parent.children[dst] = LeafNode(src=src, dst=dst)
        ops[dst] = op

    @handle_fnf
    def _branchify_leaf(self, leaf: LeafNode, terminal_src: Path) -> BranchNode:
        """Transform a leaf node into a branch node.

        The leaf node should be a directory. Only one level is expanded.
        """
        ops = self._tree.ops
        branch = BranchNode(dst=leaf.dst)

        for child_src in leaf.src.iterdir():
            if child_src == terminal_src:  # terminal node will be made by the caller
                continue

            child_dst = branch.dst / child_src.name
            node = LeafNode(src=child_src, dst=child_dst)

            branch.children[child_dst] = node
            ops[child_dst] = ops[leaf.dst]

        return branch

    def _get_dst(self, key: str, val: EntryValue | None) -> Path | None:
        """Return the resolved destination path, or None if the entry is disabled on the platform."""
        default_dst = self._paths.config_dir / key.removesuffix(".template")

        if val is None or val.dest is None:
            return default_dst

        match self._platform:
            case Platform.LINUX:
                dst = val.dest.Linux
            case Platform.WINDOWS:
                dst = val.dest.Windows

        if dst is None:
            return default_dst

        return self._paths.home / Path(dst) if dst != "" else None

    def _get_op(self, key: str, val: EntryValue | None) -> CLeafOp:
        """Return the resolved operation."""
        default_policy = Policy.RENDER if key.endswith(".template") else Policy.SYMLINK

        policy = default_policy if val is None or val.policy is None else val.policy

        match policy:
            case Policy.COPY:
                return CLeafOp.COPY
            case Policy.RENDER:
                return CLeafOp.RENDER
            case Policy.SYMLINK:
                return CLeafOp.LINK
