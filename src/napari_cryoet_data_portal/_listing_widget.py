from collections import defaultdict
from typing import TYPE_CHECKING, Dict, Generator, List, Optional, Tuple, Type

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

# Guard with type checking because this is a private import.
if TYPE_CHECKING:
    from cryoet_data_portal._gql_base import GQLExpression, GQLField


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
        
        if len(filter.spacing_ids) > 0:
            spacing_filters = _ids_to_gql_expressions(TomogramVoxelSpacing, filter.spacing_ids)
            datasets: Dict[int, Dataset] = {}
            dataset_tomograms: Dict[int, List[Tomogram]] = defaultdict(list)
            for spacing in TomogramVoxelSpacing.find(client, spacing_filters):
                dataset = spacing.run.dataset
                if (len(filter.dataset_ids) == 0) or (dataset.id in filter.dataset_ids):
                    dataset_tomograms[dataset.id].extend(spacing.tomograms)
                    datasets[dataset.id] = dataset
            for dataset_id, dataset in datasets.items():
                yield dataset, dataset_tomograms[dataset_id]
        else:
            dataset_filters = _ids_to_gql_expressions(Dataset, filter.dataset_ids)
            for dataset in Dataset.find(client, dataset_filters):
                tomograms: List[Tomogram] = []
                for run in dataset.runs:
                    for spacing in run.tomogram_voxel_spacings:
                        tomograms.extend(spacing.tomograms)
                yield dataset, tomograms

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


def _ids_to_gql_expressions(cls: Type["GQLField"], ids: Tuple[int, ...]) -> Tuple["GQLExpression", ...]:
    return () if len(ids) == 0 else (cls.id._in(ids),)
