from typing import Optional

from qtpy.QtCore import Signal
from qtpy.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QStyle,
    QVBoxLayout,
    QWidget,
)
from cryoet_data_portal import Client

from napari_cryoet_data_portal._logging import logger
from napari_cryoet_data_portal._progress_widget import ProgressWidget


GRAPHQL_URI = "https://graphql.cryoetdataportal.cziscience.com/v1/graphql"

class UriWidget(QGroupBox):
    """Connects to a data portal with a specific URI."""

    # Emitted on successful connection to the URI it contains.
    connected = Signal(object)
    # Emitted when disconnecting from the portal.
    disconnected = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.setTitle("Portal")
        self._connect_button = QPushButton("Connect")
        self._disconnect_button = QPushButton("Disconnect")
        self._uri_edit = QLineEdit(GRAPHQL_URI)
        self._uri_edit.setCursorPosition(0)
        self._uri_edit.setPlaceholderText("Enter a URI to CryoET portal data")
        choose_dir_icon = self.style().standardIcon(
            QStyle.StandardPixmap.SP_DirOpenIcon
        )
        self._choose_dir_button = QPushButton(choose_dir_icon, "")
        self._progress: ProgressWidget = ProgressWidget(
            work=self._checkUri,
            returnCallback=self._onConnected,
        )
        self._updateVisibility(False)

        self._connect_button.clicked.connect(self._onConnectClicked)
        self._disconnect_button.clicked.connect(self._onDisconnectClicked)
        self._choose_dir_button.clicked.connect(self._onChooseDirClicked)
        self._uri_edit.returnPressed.connect(self._onConnectClicked)

        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.addWidget(self._connect_button)
        control_layout.addWidget(self._disconnect_button)
        control_layout.addWidget(self._uri_edit)
        control_layout.addWidget(self._choose_dir_button)

        layout = QVBoxLayout()
        layout.addLayout(control_layout)
        layout.addWidget(self._progress)

        self.setLayout(layout)

    def _onConnectClicked(self) -> None:
        uri = self._uri_edit.text().strip()
        logger.debug("UriWidget._onConnectClicked: %s", uri)
        self._progress.submit(uri)

    def _onDisconnectClicked(self) -> None:
        logger.debug("UriWidget._onDisconnectClicked")
        self._progress.cancel()
        self._updateVisibility(False)
        self.disconnected.emit()

    def _connect(self, uri: str) -> Client:
        return Client(uri)

    def _onConnected(self, client: Client) -> None:
        logger.debug("UriWidget._onConnected: %s", client)
        self._updateVisibility(True)
        self.connected.emit(client)

    def _updateVisibility(self, uri_exists: bool) -> None:
        logger.debug("UriWidget._updateVisibility: %s", uri_exists)
        self._connect_button.setVisible(not uri_exists)
        self._choose_dir_button.setVisible(not uri_exists)
        self._disconnect_button.setVisible(uri_exists)
        self._uri_edit.setReadOnly(uri_exists)

    def _onChooseDirClicked(self) -> None:
        logger.debug("UriWidget._onChooseDirClicked")
        path = QFileDialog.getExistingDirectory(self)
        self._uri_edit.setText(path)
