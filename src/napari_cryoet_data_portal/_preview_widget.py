from typing import Generator, Optional, Tuple

import numpy as np
from qtpy.QtCore import Qt
from qtpy.QtGui import QBitmap, QIcon, QImage
from qtpy.QtWidgets import (
    QGroupBox,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)
from skimage.io import imread
from cryoet_data_portal import Client, Dataset, Run, Tomogram

from napari_cryoet_data_portal._logging import logger
from napari_cryoet_data_portal._preview_list_widget import PreviewListWidget
from napari_cryoet_data_portal._progress_widget import ProgressWidget
from napari_cryoet_data_portal._reader import read_tomogram


class PreviewWidget(QGroupBox):
    """Previews tomograms in a dataset as a list of thumbnail images."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self._uri: Optional[str] = None

        self.setTitle("Tomograms")
        self.list = PreviewListWidget()
        self._progress = ProgressWidget(
            work=self._loadTomograms,
            yieldCallback=self._onTomogramLoaded,
        )

        layout = QVBoxLayout()
        layout.addWidget(self.list, 1)
        layout.addWidget(self._progress)
        layout.addStretch(0)
        self.setLayout(layout)

    def setUri(self, uri: str) -> None:
        """Sets the URI of the portal that should be used to open preview data."""
        self._uri = uri

    def load(self, dataset: Dataset) -> None:
        """Previews the tomograms of the given dataset."""
        logger.debug("PreviewWidget.load: %s", dataset.id)
        self.list.clear()
        self.show()
        self._progress.submit(dataset)

    def cancel(self) -> None:
        """Cancels the last dataset preview load."""
        logger.debug("PreviewWidget.cancel")
        self._progress.cancel()

    def _loadTomograms(
        self, dataset: Dataset
    ) -> Generator[Tuple[Tomogram, np.ndarray], None, None]:
        logger.debug("PreviewWidget._loadTomograms: %s", dataset.id)
        client = Client(self._uri)
        for run in Run.find(client, [Run.dataset_id == dataset.id]):
            for spacing in run.tomogram_voxel_spacings:
                for tomogram in spacing.tomograms:
                    data = imread(tomogram.key_photo_thumbnail_url)
                    yield tomogram, data

    def _onTomogramLoaded(self, result: Tuple[Tomogram, np.ndarray]) -> None:
        tomogram, data = result
        logger.debug("PreviewWidget._onTomogramLoaded: %s", tomogram.name)
        icon = _make_tomogram_preview(data)
        item = QListWidgetItem(icon, tomogram.name)
        item.setData(Qt.ItemDataRole.UserRole, tomogram)
        self.list.addItem(item)


def _make_tomogram_preview(data: np.ndarray) -> QIcon:
    if data.ndim == 2:
        height, width = data.shape
        image = QImage(data.data, width, height, width, QImage.Format_Mono)
    elif data.ndim == 3:
        height, width, depth = data.shape
        assert depth == 3
        row_bytes = depth * width
        image = QImage(data.data, width, height, row_bytes, QImage.Format_RGB888)
    else:
        # TODO: at least log error.
        return QIcon()
    bitmap = QBitmap.fromImage(image)
    return QIcon(bitmap)