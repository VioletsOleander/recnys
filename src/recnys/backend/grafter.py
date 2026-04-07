from pathlib import Path

from recnys.parsing.model import BranchNode, LeafNode, Operation, RootNode, Node


class TreeGrafter:
    def graft(self, root: RootNode, prev_root: RootNode) -> RootNode:
        nodes: dict[Path, Node] = {root.dst: root}

        return root
    
    def _lookup(self,node: Node, nodes: dict[Path, Node]) -> None:
        
