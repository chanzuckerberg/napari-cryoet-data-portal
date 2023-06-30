from typing import Optional

from qtpy.QtCore import QRegularExpression
from qtpy.QtWidgets import (
    QTreeWidget,
    QWidget,
)

from napari_cryoet_data_portal._logging import logger
from napari_cryoet_data_portal._vendored.superqt._searchable_tree_widget import (
    _update_visible_items,
)


class ListingTreeWidget(QTreeWidget):
    """A filterable tree of items."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.last_filter: QRegularExpression = QRegularExpression("")

        self.setHeaderHidden(True)
        self.setDragDropMode(QTreeWidget.DragDropMode.NoDragDrop)
        self.setSelectionBehavior(QTreeWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)

    def updateVisibleItems(self, pattern: str) -> None:
        logger.debug("ListingTreeWidget.updateVisibleItems: %s", pattern)
        self.last_filter = QRegularExpression(pattern)
        for i in range(self.topLevelItemCount()):
            top_level_item = self.topLevelItem(i)
            _update_visible_items(top_level_item, self.last_filter)
