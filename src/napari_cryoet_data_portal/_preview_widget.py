from typing import Generator, Optional, Tuple

import numpy as np
from qtpy.QtCore import QSize, Qt
from qtpy.QtGui import QBitmap, QIcon
from qtpy.QtWidgets import (
    QGroupBox,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from napari_cryoet_data_portal._logging import logger
from napari_cryoet_data_portal._model import Dataset, Subject
from napari_cryoet_data_portal._preview_list_widget import PreviewListWidget
from napari_cryoet_data_portal._progress_widget import ProgressWidget
from napari_cryoet_data_portal._reader import read_tomogram_ome_zarr


class PreviewWidget(QGroupBox):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.setTitle("Preview")
        self.list = PreviewListWidget()
        self._progress = ProgressWidget(
            work=self._loadSubjects,
            yieldCallback=self._onSubjectLoaded,
        )

        layout = QVBoxLayout()
        layout.addWidget(self.list, 1)
        layout.addWidget(self._progress)
        layout.addStretch(0)
        self.setLayout(layout)

    def load(self, data: Dataset) -> None:
        logger.debug("PreviewWidget.load: %s", data.name)
        self.list.clear()
        self.show()
        self._progress.submit(data)

    def cancel(self) -> None:
        logger.debug("PreviewWidget.cancel")
        self._progress.cancel()

    def _loadSubjects(
        self, dataset: Dataset
    ) -> Generator[Tuple[Subject, np.ndarray], None, None]:
        logger.debug("PreviewWidget._loadSubjects: %s", dataset.name)
        for subject in dataset.subjects:
            data, _, _ = read_tomogram_ome_zarr(subject.image_path)
            # Materialize the lowest resolution level of the zarr for the preview.
            data = np.asarray(data[-1])
            yield subject, data

    def _onSubjectLoaded(
        self, subject_data: Tuple[Subject, np.ndarray]
    ) -> None:
        subject, data = subject_data
        logger.debug("PreviewWidget._onSubjectLoaded: %s", subject.name)
        icon = _make_tomogram_preview(data)
        item = QListWidgetItem(icon, subject.name)
        item.setData(Qt.ItemDataRole.UserRole, subject)
        self.list.addItem(item)


def _make_tomogram_preview(data: np.ndarray) -> QIcon:
    depth = data.shape[0]
    mid_data = np.asarray(data[depth // 2, :, :])
    preview_data = _normalize_data(mid_data)
    bitmap = QBitmap.fromData(
        QSize(*preview_data.shape),
        preview_data,
    )
    return QIcon(bitmap)


def _normalize_data(data: np.ndarray) -> np.ndarray:
    min_data = np.min(data)
    max_data = np.max(data)
    range_data = max_data - min_data
    if range_data == 0:
        return np.zeros(data.shape, dtype=np.uint8)
    scaled_data = 255 * (data - min_data) / range_data
    return scaled_data.astype(np.uint8)
