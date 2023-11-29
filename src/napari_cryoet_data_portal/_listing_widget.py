from collections import defaultdict
from typing import Dict, Generator, List, Optional, Tuple

from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QGroupBox,
    QLineEdit,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)
from cryoet_data_portal import Client, Dataset, Tomogram, TomogramVoxelSpacing

from napari_cryoet_data_portal._filter import Filter
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

        self.setTitle("Data")
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

    def load(self, uri: str, *, filter: Filter = Filter()) -> None:
        """Lists the datasets and tomograms using the given portal URI."""
        logger.debug("ListingWidget.load: %s, %s", uri, filter)
        self.tree.clear()
        self.show()
        self._progress.submit(uri, filter)

    def cancel(self) -> None:
        """Cancels the last listing."""
        logger.debug("ListingWidget.cancel")
        self._progress.cancel()

    def _loadDatasets(self, uri: str, filter: Filter) -> Generator[Tuple[Dataset, List[Tomogram]], None, None]:
        logger.debug("ListingWidget._loadDatasets: %s", uri)
        client = Client(uri)
        
        if (filter.type is Dataset) or (len(filter.ids) == 0):
            yield from _load_datasets(client, filter)
        elif filter.type is TomogramVoxelSpacing:
            yield from _load_datasets_from_spacings(client, filter)
        elif filter.type is Tomogram:
            yield from _load_datasets_from_tomograms(client, filter)

    def _onDatasetLoaded(self, result: Tuple[Dataset, List[Tomogram]]) -> None:
        dataset, tomograms = result
        logger.debug("ListingWidget._onDatasetLoaded: %s", dataset.id)
        text = f"{dataset.id} ({len(tomograms)})"
        item = QTreeWidgetItem((text,))
        item.setData(0, Qt.ItemDataRole.UserRole, dataset)
        for tomogram in tomograms:
            tomogram_item = QTreeWidgetItem((tomogram.name,))
            tomogram_item.setData(0, Qt.ItemDataRole.UserRole, tomogram)
            item.addChild(tomogram_item)
        _update_visible_items(item, self.tree.last_filter)
        self.tree.addTopLevelItem(item)


def _load_datasets(client: Client, filter: Filter) -> Generator[Tuple[Dataset, List[Tomogram]], None, None]:
    assert filter.type is Dataset
    for dataset in Dataset.find(client, filter.to_gql()):
        tomograms: List[Tomogram] = []
        for run in dataset.runs:
            for spacing in run.tomogram_voxel_spacings:
                tomograms.extend(spacing.tomograms)
        yield dataset, tomograms


def _load_datasets_from_tomograms(client: Client, filter: Filter) -> Generator[Tuple[Dataset, List[Tomogram]], None, None]:
    assert filter.type is Tomogram
    datasets: Dict[int, Dataset] = {}
    tomograms: Dict[int, List[Tomogram]] = defaultdict(list)
    for tomogram in Tomogram.find(client, filter.to_gql()):
        dataset = tomogram.tomogram_voxel_spacing.run.dataset
        datasets[dataset.id] = dataset
        tomograms[dataset.id].append(tomogram)
    for i in datasets:
        yield datasets[i], tomograms[i]


def _load_datasets_from_spacings(client: Client, filter: Filter) -> Generator[Tuple[Dataset, List[Tomogram]], None, None]:
    assert filter.type is TomogramVoxelSpacing
    datasets: Dict[int, Dataset] = {}
    tomograms: Dict[int, List[Tomogram]] = defaultdict(list)
    for spacing in TomogramVoxelSpacing.find(client, filter.to_gql()):
        dataset = spacing.run.dataset
        datasets[dataset.id] = dataset
        tomograms[dataset.id].extend(spacing.tomograms)
    for i in datasets:
        yield datasets[i], tomograms[i]
