"""Provide `DTreeBuilder`."""

from typing import TYPE_CHECKING

from .deriver import DTreeDeriver

if TYPE_CHECKING:
    from recnys.backend.ctree.model import CRootNode

    from .model import DRootNode

__all__ = ["DTreeBuilder"]


class DTreeBuilder:
    """DTreeBuilder builds the deletion tree to execute.

    Recnys stores `prev_ctree` and `prev_dtree` constructed during the execution process. The execution
    process executes ctree from top-down, and executes dtree from bottom-up, and construct the final ctree
    by adding nodes, construct the final dtree by deleting nodes.

    Therefore, during the execution process, the final ctree to store will be created from top-down,
    with the built ctree as reference and the final dtree to store will be created from bottom-up,
    with the built dtree as reference.

    Since dtree is executed before ctree, and once interrupted, program will exit, therefore, depending
    on the execution situation, the valid states of the `prev_ctree` and `prev_dtree` includes:

    - Deletion and Creation both successfully executed:
        `prev_dtree` is an empty root, `prev_ctree` is a full tree the same as the built ctree
    - Deletion successfully executed, creation interrupted:
        `prev_dtree` is an empty root, `prev_ctree` is a partial tree compared to the built ctree
    - Deletion interrupted, creation not executed at all:
        `prev_dtree` is a partial tree compared to the built dtree, `prev_ctree` is an empty root
    - Deletion and creation both not executed at all:
        `prev_dtree` is a full tree the same as the built dtree, `prev_ctree` is an empty root

    If `prev_ctree` is an empty root, we do not need to derive a dtree, the dtree to execute is just
    `prev_dtree`.
    If `prev_ctree` is not an empty root, `prev_dtree` will be an empty rot, and we need to derive a
    dtree, the dtree to execute is the derived dtree.
    """

    def build(self, ctree: CRootNode, prev_ctree: CRootNode, prev_dtree: DRootNode) -> DRootNode:
        """Build a deletion tree to execute based on the built ctree and the previous ctree and dtree.

        Args:
            ctree (CRootNode): The built creation tree.
            prev_ctree (CRootNode): The previous creation tree.
            prev_dtree (DRootNode): The previous deletion tree.

        Returns:
            DRootNode: The root node of the deletion tree to execute.
        """
        ctree_empty = not prev_ctree.children
        dtree_empty = not prev_dtree.children

        if ctree_empty == dtree_empty:
            e = RuntimeError("Ctree file and dtree file does not met the expected state.")
            e.add_note(
                "Hint: Please use backup file to recover them. "
                "If backup file is not available, please delete them."
            )
            raise e

        if dtree_empty:
            deriver = DTreeDeriver()
            dtree = deriver.derive(ctree, prev_ctree)
        else:
            dtree = prev_dtree

        return dtree
