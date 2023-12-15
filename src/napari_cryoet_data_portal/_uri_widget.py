from typing import Optional, Tuple

from qtpy.QtCore import Signal
from qtpy.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from cryoet_data_portal import Client, Dataset, Run, Tomogram, TomogramVoxelSpacing

from napari_cryoet_data_portal._filter import Filter, make_filter
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
        
        filter_ids_layout = QHBoxLayout()
        filter_ids_layout.setContentsMargins(0, 0, 0, 0)
        self._filter_ids_type = QComboBox()
        self._filter_ids_type.addItem("Dataset IDs", Dataset)
        self._filter_ids_type.addItem("Run IDs", Run)
        self._filter_ids_type.addItem("Voxel Spacing IDs", TomogramVoxelSpacing)
        self._filter_ids_type.addItem("Tomogram IDs", Tomogram)
        self._filter_ids_edit = QLineEdit()
        self._filter_ids_edit.setToolTip("Comma separated IDs of interest")
        filter_ids_layout.addWidget(self._filter_ids_type)
        filter_ids_layout.addWidget(self._filter_ids_edit)
        
        self._progress: ProgressWidget = ProgressWidget(
            work=self._connect,
            returnCallback=self._onConnected,
        )
        self._updateVisibility(False)

        self._connect_button.clicked.connect(self._onConnectClicked)
        self._disconnect_button.clicked.connect(self._onDisconnectClicked)
        self._uri_edit.returnPressed.connect(self._onConnectClicked)
        self._filter_ids_edit.returnPressed.connect(self._onConnectClicked)

        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.addWidget(self._connect_button)
        control_layout.addWidget(self._disconnect_button)
        control_layout.addWidget(self._uri_edit)

        layout = QVBoxLayout()
        layout.addLayout(control_layout)
        layout.addLayout(filter_ids_layout)
        layout.addWidget(self._progress)

        self.setLayout(layout)

    def _onConnectClicked(self) -> None:
        uri = self._uri_edit.text().strip()
        filter_ids = _csv_to_ids(self._filter_ids_edit.text())
        filter = make_filter(
            self._filter_ids_type.currentData(),
            ids=filter_ids,
        )
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
        self._filter_ids_type.setDisabled(uri_exists)
        self._filter_ids_edit.setReadOnly(uri_exists)
        self._disconnect_button.setVisible(uri_exists)


def _csv_to_ids(csv: str) -> Tuple[int, ...]:
    ids: Tuple[int, ...] = ()
    csv = csv.strip()
    if len(csv) > 0:
        try:
            names = csv.split(",")
            ids = tuple(int(name) for name in names)
        except ValueError as e:
            raise ValueError(f"Failed to parse numeric IDs: {csv}") from e
    return ids
