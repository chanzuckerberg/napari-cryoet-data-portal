from typing import Optional, Tuple

from qtpy.QtCore import Signal
from qtpy.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from cryoet_data_portal import Client

from napari_cryoet_data_portal._filter import Filter
from napari_cryoet_data_portal._logging import logger
from napari_cryoet_data_portal._progress_widget import ProgressWidget


GRAPHQL_URI = "https://graphql.cryoetdataportal.cziscience.com/v1/graphql"

class UriWidget(QGroupBox):
    """Connects to a data portal with a specific URI."""

    # Emitted on successful connection with the URI.
    connected = Signal(str, object)
    # Emitted when disconnecting from the portal.
    disconnected = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.setTitle("Portal")
        self._connect_button = QPushButton("Connect")
        self._disconnect_button = QPushButton("Disconnect")

        self._uri_edit = QLineEdit(GRAPHQL_URI)
        # Only allow the default portal URI because invalid ones will cause
        # indefinite hangs:
        # https://github.com/chanzuckerberg/cryoet-data-portal/issues/16
        self._uri_edit.setReadOnly(True)
        self._uri_edit.setCursorPosition(0)
        self._uri_edit.setPlaceholderText("Enter a URI to CryoET portal data")
        
        self._dataset_ids_edit, dataset_widget = _make_labeled_edit(
            "Dataset IDs", "Comma separated dataset IDs query")
        self._spacing_ids_edit, spacing_widget = _make_labeled_edit(
            "Voxel Spacing IDs", "Comma separated voxel spacing IDs to query")

        self._progress: ProgressWidget = ProgressWidget(
            work=self._connect,
            returnCallback=self._onConnected,
        )
        self._updateVisibility(False)

        self._connect_button.clicked.connect(self._onConnectClicked)
        self._disconnect_button.clicked.connect(self._onDisconnectClicked)
        self._uri_edit.returnPressed.connect(self._onConnectClicked)
        self._dataset_ids_edit.returnPressed.connect(self._onConnectClicked)
        self._spacing_ids_edit.returnPressed.connect(self._onConnectClicked)

        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.addWidget(self._connect_button)
        control_layout.addWidget(self._disconnect_button)
        control_layout.addWidget(self._uri_edit)

        layout = QVBoxLayout()
        layout.addLayout(control_layout)
        layout.addWidget(dataset_widget)
        layout.addWidget(spacing_widget)
        layout.addWidget(self._progress)

        self.setLayout(layout)

    def _onConnectClicked(self) -> None:
        uri = self._uri_edit.text().strip()
        datasets = self._dataset_ids_edit.text()
        spacings = self._spacing_ids_edit.text()
        filter = Filter.from_csv(datasets=datasets, spacings=spacings)
        logger.debug("UriWidget._onConnectClicked: %s, %s", uri, filter)
        self._progress.submit(uri, filter)

    def _onDisconnectClicked(self) -> None:
        logger.debug("UriWidget._onDisconnectClicked")
        self._progress.cancel()
        self._updateVisibility(False)
        self.disconnected.emit()

    def _connect(self, uri: str, filter: Filter) -> Tuple[str, Filter]:
        _ = Client(uri)
        return uri, filter

    def _onConnected(self, result: Tuple[str, Filter]) -> None:
        uri, filter = result
        logger.debug("UriWidget._onConnected: %s, %s", uri, filter)
        self._updateVisibility(True)
        self.connected.emit(uri, filter)

    def _updateVisibility(self, uri_exists: bool) -> None:
        logger.debug("UriWidget._updateVisibility: %s", uri_exists)
        self._connect_button.setVisible(not uri_exists)
        self._dataset_ids_edit.setReadOnly(uri_exists)
        self._spacing_ids_edit.setReadOnly(uri_exists)
        self._disconnect_button.setVisible(uri_exists)


def _make_labeled_edit(label: str, tooltip: str) -> Tuple[QLineEdit, QWidget]:
    main_widget = QWidget()
    edit_widget = QLineEdit()
    label_widget = QLabel(label)
    main_widget.setToolTip(tooltip)
    layout = QHBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    main_widget.setLayout(layout)
    layout.addWidget(label_widget)
    layout.addWidget(edit_widget)
    return edit_widget, main_widget
