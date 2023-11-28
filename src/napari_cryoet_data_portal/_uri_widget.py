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
        
        dataset_layout = QHBoxLayout()
        dataset_layout.setContentsMargins(0, 0, 0, 0)
        self._dataset_id_edit = QLineEdit()
        dataset_id_label = QLabel("Dataset ID")
        dataset_id_label.setBuddy(self._dataset_id_edit)
        dataset_layout.addWidget(dataset_id_label)
        dataset_layout.addWidget(self._dataset_id_edit)
        
        tomo_layout = QHBoxLayout()
        tomo_layout.setContentsMargins(0, 0, 0, 0)
        self._tomo_id_edit = QLineEdit()
        tomo_id_label = QLabel("Voxel spacing ID")
        tomo_id_label.setBuddy(self._tomo_id_edit)
        tomo_layout.addWidget(tomo_id_label)
        tomo_layout.addWidget(self._tomo_id_edit)

        self._progress: ProgressWidget = ProgressWidget(
            work=self._connect,
            returnCallback=self._onConnected,
        )
        self._updateVisibility(False)

        self._connect_button.clicked.connect(self._onConnectClicked)
        self._disconnect_button.clicked.connect(self._onDisconnectClicked)
        self._uri_edit.returnPressed.connect(self._onConnectClicked)
        self._tomo_id_edit.returnPressed.connect(self._onConnectClicked)
        self._dataset_id_edit.returnPressed.connect(self._onConnectClicked)

        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.addWidget(self._connect_button)
        control_layout.addWidget(self._disconnect_button)
        control_layout.addWidget(self._uri_edit)

        layout = QVBoxLayout()
        layout.addLayout(control_layout)
        layout.addLayout(dataset_layout)
        layout.addLayout(tomo_layout)
        layout.addWidget(self._progress)

        self.setLayout(layout)

    def _onConnectClicked(self) -> None:
        uri = self._uri_edit.text().strip()
        dataset = self._dataset_id_edit.text().strip()
        spacing = self._tomo_id_edit.text().strip()
        filter = Filter.from_names(dataset=dataset, spacing=spacing)
        logger.debug("UriWidget._onConnectClicked: %s, %s", uri, filter)
        self._progress.submit(uri, filter)

    def _onDisconnectClicked(self) -> None:
        logger.debug("UriWidget._onDisconnectClicked")
        self._progress.cancel()
        self._updateVisibility(False)
        self.disconnected.emit()

    def _connect(self, uri: str, filter: Filter) -> Tuple[str, object]:
        _ = Client(uri)
        return uri, filter

    def _onConnected(self, result: Tuple[str, object]) -> None:
        uri, filter = result
        logger.debug("UriWidget._onConnected: %s, %s", uri, filter)
        self._updateVisibility(True)
        self.connected.emit(uri, filter)

    def _updateVisibility(self, uri_exists: bool) -> None:
        logger.debug("UriWidget._updateVisibility: %s", uri_exists)
        self._connect_button.setVisible(not uri_exists)
        self._dataset_id_edit.setReadOnly(uri_exists)
        self._tomo_id_edit.setReadOnly(uri_exists)
        self._disconnect_button.setVisible(uri_exists)
