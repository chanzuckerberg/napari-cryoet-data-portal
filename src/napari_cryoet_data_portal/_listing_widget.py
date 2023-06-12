from typing import Generator, Optional

from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QGroupBox,
    QLineEdit,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from napari_cryoet_data_portal._io import list_dir
from napari_cryoet_data_portal._listing_tree_widget import ListingTreeWidget
from napari_cryoet_data_portal._logging import logger
from napari_cryoet_data_portal._model import Dataset
from napari_cryoet_data_portal._progress_widget import ProgressWidget
from napari_cryoet_data_portal._vendored.superqt._searchable_tree_widget import (
    _update_visible_items,
)


class ListingWidget(QGroupBox):
    """Lists the datasets and tomograms in a searchable tree."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.setTitle("Data")
        self.tree = ListingTreeWidget()
        self.filter = QLineEdit()
        self.filter.setPlaceholderText("Filter datasets and tomograms")
        self.filter.setClearButtonEnabled(True)
        self._progress = ProgressWidget(
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

    def load(self, path: str) -> None:
        """Lists the datasets and tomograms at the given data portal path."""
        logger.debug("ListingWidget.load: %s", path)
        self.tree.clear()
        self.show()
        self._progress.submit(path)

    def cancel(self) -> None:
        """Cancels the last listing."""
        logger.debug("ListingWidget.cancel")
        self._progress.cancel()

    def _loadDatasets(self, path: str) -> Generator[Dataset, None, None]:
        logger.debug("ListingWidget._loadDatasets: %s", path)
        # TODO: only list non-hidden directories.
        dataset_names = tuple(
            p for p in list_dir(path) if not p.startswith(".")
        )
        if len(dataset_names) == 0:
            logger.debug("No datasets found")
        for name in dataset_names:
            yield Dataset.from_data_path_and_name(path, name)

    def _onDatasetLoaded(self, dataset: Dataset) -> None:
        logger.debug("ListingWidget._onDatasetLoaded: %s", dataset.name)
        text = f"{dataset.name} ({len(dataset.subjects)})"
        item = QTreeWidgetItem((text,))
        item.setData(0, Qt.ItemDataRole.UserRole, dataset)
        for s in dataset.subjects:
            subject_item = QTreeWidgetItem((s.name,))
            subject_item.setData(0, Qt.ItemDataRole.UserRole, s)
            item.addChild(subject_item)
        _update_visible_items(item, self.tree.last_filter)
        self.tree.addTopLevelItem(item)
