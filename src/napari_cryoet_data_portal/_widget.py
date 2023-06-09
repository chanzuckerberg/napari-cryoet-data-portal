from typing import TYPE_CHECKING, Optional

from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from napari_cryoet_data_portal._listing_widget import ListingWidget
from napari_cryoet_data_portal._logging import logger
from napari_cryoet_data_portal._metadata_widget import MetadataWidget
from napari_cryoet_data_portal._model import Subject
from napari_cryoet_data_portal._open_widget import OpenWidget
from napari_cryoet_data_portal._uri_widget import UriWidget

if TYPE_CHECKING:
    from napari.components import ViewerModel


class DataPortalWidget(QWidget):
    """The main widget for browsing the data portal from napari."""

    def __init__(
        self, napari_viewer: "ViewerModel", parent: Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)

        self._uri = UriWidget()

        self._listing = ListingWidget()
        self._listing.hide()

        self._metadata = MetadataWidget()
        self._metadata.hide()

        self._open = OpenWidget(napari_viewer)
        self._open.hide()

        self._uri.connected.connect(self._onUriConnected)
        self._uri.disconnected.connect(self._onUriDisconnected)
        self._listing.tree.currentItemChanged.connect(
            self._onListingItemChanged
        )

        layout = QVBoxLayout()
        layout.addWidget(self._uri)
        layout.addWidget(self._listing, 1)
        layout.addWidget(self._metadata, 1)
        layout.addWidget(self._open)
        layout.addStretch(0)

        self.setLayout(layout)

    def _onUriConnected(self, uri: str) -> None:
        logger.debug("DataPortalWidget._onUriConnected")
        self._listing.load(uri)

    def _onUriDisconnected(self) -> None:
        logger.debug("DataPortalWidget._onUriDisconnected")
        for widget in (self._listing, self._metadata, self._open):
            widget.cancel()
            widget.hide()

    def _onListingItemChanged(
        self, item: QTreeWidgetItem, old_item: QTreeWidgetItem
    ) -> None:
        logger.debug("DataPortalWidget._onListingItemClicked: %s", item)
        # The new current item can be none when reconnecting since that
        # clears the listing tree.
        if item is None:
            self._metadata.hide()
            self._open.hide()
            return
        data = item.data(0, Qt.ItemDataRole.UserRole)
        self._metadata.load(data)
        if isinstance(data, Subject):
            self._open.setSubject(data)
        else:
            self._open.hide()
