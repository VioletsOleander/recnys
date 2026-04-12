"""Provide `DTreeBuilder`."""

import logging
from typing import TYPE_CHECKING

from .deriver import DTreeDeriver

if TYPE_CHECKING:
    from recnys.tree.model import CTree, DTree

__all__ = ["DTreeBuilder"]

logger = logging.getLogger(__name__)


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

    def build(self, ctree: CTree, prev_ctree: CTree, prev_dtree: DTree) -> DTree:
        """Build a deletion tree to execute based on the built ctree and the previous ctree and dtree.

        Args:
            ctree (CTree): The built creation tree.
            prev_ctree (CTree): The previous creation tree.
            prev_dtree (DTree): The previous deletion tree.

        Returns:
            DTree: The root node of the deletion tree to execute.
        """
        logger.debug("Building deletion tree.")

        ctree_empty = not prev_ctree.root.children
        dtree_empty = not prev_dtree.root.children

        if ctree_empty == dtree_empty:
            raise RuntimeError(
                "Ctree file and dtree file does not meet the expected state.\n"
                "Hint: Please use backup file to recover them. "
                "If backup file is not available, please delete them."
            )

        if dtree_empty:
            logger.debug("Previous ctree is not empty, derive deletion tree from it.")
            deriver = DTreeDeriver()
            dtree = deriver.derive(ctree, prev_ctree)
        else:
            logger.debug(
                "Previous ctree is empty, use previous dtree as the deletion tree to execute."
            )
            dtree = prev_dtree

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Built deletion tree: %s", dtree.model_dump_json(indent=2))

        return dtree
