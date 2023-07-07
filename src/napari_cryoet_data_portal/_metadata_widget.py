from typing import Any, Dict, Optional, Union

from qtpy.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
    QWidget,
)
from cryoet_data_portal import Dataset, Tomogram

from napari_cryoet_data_portal._logging import logger
from napari_cryoet_data_portal._progress_widget import ProgressWidget
from napari_cryoet_data_portal._vendored.superqt._searchable_tree_widget import (
    QSearchableTreeWidget,
)


class MetadataWidget(QGroupBox):
    """Displays the JSON metadata of a dataset or tomogram in the portal."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self._main = QSearchableTreeWidget()
        self._main.layout().setContentsMargins(0, 0, 0, 0)
        self._main.filter.setPlaceholderText("Filter metadata")
        self._progress: ProgressWidget = ProgressWidget(
            work=self._loadMetadata,
            returnCallback=self._onMetadataLoaded,
        )

        layout = QVBoxLayout()
        layout.addWidget(self._main, 1)
        layout.addWidget(self._progress)
        layout.addStretch(0)
        self.setLayout(layout)

    def load(self, data: Union[Dataset, Tomogram]) -> None:
        """Loads the JSON metadata of the given dataset or tomogram."""
        logger.debug("MetadataWidget.load: %s", data)
        self._main.tree.clear()
        name = data.id if isinstance(data, Dataset) else data.name
        self.setTitle(f"Metadata: {name}")
        self.show()
        self._progress.submit(data)

    def cancel(self) -> None:
        """Cancels the last metadata load."""
        logger.debug("MetadataWidget.cancel")
        self._progress.cancel()

    def _loadMetadata(self, data: Union[Dataset, Tomogram]) -> Dict[str, Any]:
        logger.debug("MetadataWidget._loadMetadata: %s", data)
        return data.to_dict()

    def _onMetadataLoaded(self, metadata: Dict[str, Any]) -> None:
        logger.debug("MetadataWidget._onMetadataLoaded: %s", metadata)
        self._main.setData(metadata)
