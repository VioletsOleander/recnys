"""Provide `ConfigParser`."""

from pathlib import Path
from typing import TYPE_CHECKING

from recnys.scanning.model import EntryValue, Policy, ScannedConfig
from recnys.utils.platform import Platform

from .model import BranchNode, LeafNode, Operation, RootNode

if TYPE_CHECKING:
    from recnys.utils.paths import Paths

__all__ = ["ConfigParser"]


class ConfigParser:
    """ConfigParser parses the scanned configuration into a node tree structure.

    During the parsing process, features from features/deconflict are satisfied.

    The main provided method is `parse`.
    """

    paths: Paths
    platform: Platform

    def __init__(self, paths: Paths, platform: Platform) -> None:
        """Initialize the ConfigParser.

        Args:
            paths (Paths): The Paths instance containing relevant paths.
            platform (Platform): The current platform.
        """
        self.paths = paths
        self.platform = platform

    def parse(self, scanned_config: ScannedConfig) -> RootNode:
        """Construct a node tree from the scanned configuration.

        Args:
            scanned_config (ScannedConfig): The scanned configuration to be parsed.

        Returns:
            RootNode: The root node of the constructed node tree.
        """
        root = RootNode(dst=self.paths.home)

        for key, val in scanned_config.root.items():
            dst = self._get_dst(key, val)
            if dst is None:
                continue

            src = self.paths.repo_dir / key
            op = self._get_op(key, val)
            self._make_nodes(src=src, dst=dst, op=op, root=root)

        return root

    def _make_nodes(self, src: Path, dst: Path, op: Operation, root: RootNode) -> None:
        """Make branch and leaf nodes.

        Conflict leaf nodes will be recursively branchified.

        All features specified in features/deconflict are satisfied by this implementation.
        """
        parent = root
        for branch_dst in dst.parents[:-1]:  # exclude home
            if branch_dst in parent.children:
                node = parent.children[branch_dst]
                branch = self._branchify_leaf(node) if isinstance(node, LeafNode) else node
            else:
                branch = BranchNode(dst=branch_dst)

            parent.children[branch_dst] = branch
            parent = branch

        leaf = LeafNode(src=src, dst=dst, op=op)
        parent.children[dst] = leaf

    def _branchify_leaf(self, leaf: LeafNode) -> BranchNode:
        """Transform a leaf node into a branch node.

        The leaf node should be a directory.
        """
        branch = BranchNode(dst=leaf.dst)

        for child_src, child_dst in zip(leaf.src.iterdir(), leaf.dst.iterdir(), strict=True):
            node = LeafNode(src=child_src, dst=child_dst, op=leaf.op)
            branch.children[child_dst] = node

        return branch

    def _get_dst(self, key: str, val: EntryValue | None) -> Path | None:
        """Return the resolved destination path, or None if the entry is disabled on the platform."""
        default_dst = self.paths.config_dir / key.removesuffix(".template")

        if val is None or val.dest is None:
            return default_dst

        match self.platform:
            case Platform.LINUX:
                dst = val.dest.Linux
                if dst is None:
                    return default_dst

                return None if dst == "" else Path(dst)
            case Platform.WINDOWS:
                dst = val.dest.Windows
                if dst is None:
                    return default_dst

                return None if dst == "" else Path(dst)

    def _get_op(self, key: str, val: EntryValue | None) -> Operation:
        """Return the resolved operation."""
        default_policy = Policy.RENDER if key.endswith(".template") else Policy.SYMLINK

        policy = default_policy if val is None or val.policy is None else val.policy

        match policy:
            case Policy.COPY:
                return Operation.COPY
            case Policy.RENDER:
                return Operation.RENDER
            case Policy.SYMLINK:
                return Operation.LINK
