from typing import Optional

from qtpy.QtCore import QRegularExpression, QSize
from qtpy.QtWidgets import (
    QListWidget,
    QListWidgetItem,
    QWidget,
)

from napari_cryoet_data_portal._logging import logger


class PreviewListWidget(QListWidget):
    """Lists subjects by showing a preview of their image."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self._last_filter: QRegularExpression = QRegularExpression("")

        self.setViewMode(QListWidget.ViewMode.IconMode)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.setFlow(QListWidget.Flow.LeftToRight)
        self.setDragEnabled(False)
        self.setAcceptDrops(False)
        self.setIconSize(QSize(64, 64))

    def addItem(self, item: QListWidgetItem) -> None:
        logger.debug("PreviewListWidget.addItem: %s", item)
        _update_visible_item(item, self._last_filter)
        super().addItem(item)

    def updateVisibleItems(self, pattern: str) -> None:
        logger.debug("PreviewListWidget.updateVisibleItems: %s", pattern)
        self._last_filter = QRegularExpression(pattern)
        for i in range(self.count()):
            item = self.item(i)
            _update_visible_item(item, self._last_filter)


def _update_visible_item(
    item: QListWidgetItem, expression: QRegularExpression
) -> None:
    text = item.text()
    visible = expression.match(text).hasMatch()
    item.setHidden(not visible)
