from dataclasses import dataclass
from typing import TYPE_CHECKING, Generator, Optional, Tuple

import numpy as np
from npe2.types import FullLayerData
from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from napari_cryoet_data_portal._logging import logger
from napari_cryoet_data_portal._model import Subject
from napari_cryoet_data_portal._progress_widget import ProgressWidget
from napari_cryoet_data_portal._reader import (
    read_points_annotations_json,
    read_tomogram_ome_zarr,
)

if TYPE_CHECKING:
    from napari.components import ViewerModel


# TODO: read these from metadata instead of hard-coding them.
@dataclass
class Resolution:
    name: str
    indices: Tuple[int, ...]
    scale: float


MULTI_RESOLUTION = Resolution(name="Multi", indices=(0, 1, 2), scale=1)
HIGH_RESOLUTION = Resolution(name="High", indices=(0,), scale=1)
MID_RESOLUTION = Resolution(name="Mid", indices=(1,), scale=2)
LOW_RESOLUTION = Resolution(name="Low", indices=(2,), scale=4)

RESOLUTIONS: Tuple[Resolution] = (
    MULTI_RESOLUTION,
    HIGH_RESOLUTION,
    MID_RESOLUTION,
    LOW_RESOLUTION,
)


class OpenWidget(QGroupBox):
    """Opens a tomogram and its annotations at a specific resolution."""

    def __init__(
        self, viewer: "ViewerModel", parent: Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)

        self._viewer = viewer
        self._subject: Optional[Subject] = None

        self.setTitle("Tomogram")

        self.open = QPushButton("Open")
        self.resolution_label = QLabel("Resolution")
        self.resolution_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.resolution = QComboBox()
        for res in RESOLUTIONS:
            self.resolution.addItem(res.name, res)
        self.resolution.setCurrentText(LOW_RESOLUTION.name)
        self.resolution_label.setBuddy(self.resolution)
        self._progress = ProgressWidget(
            work=self._loadSubject,
            yieldCallback=self._onLayerLoaded,
        )

        self.open.clicked.connect(self.load)

        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.addWidget(self.open)
        control_layout.addWidget(self.resolution_label)
        control_layout.addWidget(self.resolution)

        layout = QVBoxLayout()
        layout.addLayout(control_layout)
        layout.addWidget(self._progress)
        self.setLayout(layout)

    def setSubject(self, subject: Subject) -> None:
        """Sets the current tomogram that should be opened."""
        self.cancel()
        self._subject = subject
        # Reset resolution to low to handle case when user tries
        # out a higher resolution but then moves onto another tomogram.
        self.resolution.setCurrentText(LOW_RESOLUTION.name)
        self.setTitle(f"Tomogram: {subject.name}")
        self.show()
        self.load()

    def load(self) -> None:
        """Loads the current tomogram at the current resolution."""
        resolution = self.resolution.currentData()
        logger.debug("OpenWidget.load: %s", self._subject, resolution)
        self._viewer.layers.clear()
        self._progress.submit(self._subject, resolution)

    def cancel(self) -> None:
        """Cancels the last tomogram load."""
        logger.debug("OpenWidget.cancel")
        self._progress.cancel()

    def _loadSubject(
        self,
        subject: Subject,
        resolution: Resolution,
    ) -> Generator[FullLayerData, None, None]:
        logger.debug("OpenWidget._loadSubject: %s", subject.name)
        image_data, image_attrs, _ = read_tomogram_ome_zarr(subject.image_path)
        # TODO: read JSON metadata in reader to get name from there.
        image_attrs["name"] = f"{subject.name}-tomogram"
        # Skip indexing for multi-resolution to avoid adding any
        # unnecessary nodes to the dask compute graph.
        if resolution is not MULTI_RESOLUTION:
            image_data = image_data[resolution.indices[0]]
        # Materialize low resolution immediately on this thread to prevent napari blocking.
        if resolution is LOW_RESOLUTION:
            image_data = np.asarray(image_data)
        image_attrs["scale"] = tuple(
            resolution.scale * s for s in image_attrs["scale"]
        )
        yield image_data, image_attrs, "image"

        for p in subject.annotation_paths:
            points_data, points_attrs, _ = read_points_annotations_json(p)
            annotation_name = points_attrs["name"]
            points_attrs["name"] = f"{subject.name}-{annotation_name}"
            yield points_data, points_attrs, "points"

        return subject

    def _onLayerLoaded(self, layer_data: FullLayerData) -> None:
        logger.debug("OpenWidget._onLayerLoaded")
        data, attrs, layer_type = layer_data
        if layer_type == "image":
            self._viewer.add_image(data, **attrs)
        elif layer_type == "points":
            self._viewer.add_points(data, **attrs)
        else:
            raise AssertionError(f"Unexpected {layer_type=}")
