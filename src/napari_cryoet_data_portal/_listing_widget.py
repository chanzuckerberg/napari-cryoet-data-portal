from typing import Generator, List, Optional, Tuple

from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QGroupBox,
    QLineEdit,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)
from cryoet_data_portal import Client, Dataset, Tomogram

from napari_cryoet_data_portal._listing_tree_widget import ListingTreeWidget
from napari_cryoet_data_portal._logging import logger
from napari_cryoet_data_portal._progress_widget import ProgressWidget
from napari_cryoet_data_portal._vendored.superqt._searchable_tree_widget import (
    _update_visible_items,
)


class ListingWidget(QGroupBox):
    """Lists the datasets and tomograms in a searchable tree."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.setTitle("Datasets")
        self.tree = ListingTreeWidget()
        self.filter = QLineEdit()
        self.filter.setPlaceholderText("Filter datasets and tomograms")
        self.filter.setClearButtonEnabled(True)
        self._progress: ProgressWidget = ProgressWidget(
            work=self._loadDatasets,
            yieldCallback=self._onDatasetLoaded,
        )

        self.filter.textChanged.connect(self.tree.updateVisibleItems)

        layout = QVBoxLayout()
        layout.addWidget(self.filter)
        layout.addWidget(self.tree, 1)
        layout.addWidget(self._progress)
        layout.addStretch(0)
        self.setLayout(layout)

    def load(self, uri: str) -> None:
        """Lists the datasets and tomograms using the given portal URI."""
        logger.debug("ListingWidget.load: %s", uri)
        self.tree.clear()
        self.show()
        self._progress.submit(uri)

    def cancel(self) -> None:
        """Cancels the last listing."""
        logger.debug("ListingWidget.cancel")
        self._progress.cancel()

    def _loadDatasets(self, uri: str) -> Generator[Dataset, None, None]:
        logger.debug("ListingWidget._loadDatasets: %s", uri)
        client = Client(uri)
        yield from Dataset.find(client)

    def _onDatasetLoaded(self, dataset: Dataset) -> None:
        logger.debug("ListingWidget._onDatasetLoaded: %s", dataset.id)
        text = f"{dataset.id}"
        item = QTreeWidgetItem((text,))
        item.setData(0, Qt.ItemDataRole.UserRole, dataset)
        _update_visible_items(item, self.tree.last_filter)
        self.tree.addTopLevelItem(item)
