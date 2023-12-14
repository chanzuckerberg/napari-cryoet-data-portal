from dataclasses import dataclass
from typing import TYPE_CHECKING, Generator, Optional, Tuple

import numpy as np
from npe2.types import FullLayerData
from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from cryoet_data_portal import Annotation, Client, Tomogram

from napari_cryoet_data_portal._logging import logger
from napari_cryoet_data_portal._progress_widget import ProgressWidget
from napari_cryoet_data_portal._reader import (
    read_annotation,
    read_tomogram,
)

if TYPE_CHECKING:
    from napari.components import ViewerModel


# TODO: read these from metadata instead of hard-coding them.
@dataclass
class Resolution:
    name: str
    indices: Tuple[int, ...]
    scale: float

    @property
    def offset(self) -> float:
        """The offset due to a larger first pixel for lower resolutions.

        When visualized in napari, this ensures that the different multi-scale
        layers opened separately share the same visual extent in the canvas that
        starts at (-0.5, -0.5, -0.5).
        """
        return (self.scale - 1) / 2


MULTI_RESOLUTION = Resolution(name="Multi", indices=(0, 1, 2), scale=1)
HIGH_RESOLUTION = Resolution(name="High", indices=(0,), scale=1)
MID_RESOLUTION = Resolution(name="Mid", indices=(1,), scale=2)
LOW_RESOLUTION = Resolution(name="Low", indices=(2,), scale=4)

RESOLUTIONS: Tuple[Resolution, ...] = (
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
        self._uri: Optional[str] = None
        self._tomogram: Optional[Tomogram] = None

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
        self._progress: ProgressWidget = ProgressWidget(
            work=self._loadTomogram,
            yieldCallback=self._onLayerLoaded,
        )

        self.open.clicked.connect(self.load)

        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.addWidget(self.open)
        control_layout.addWidget(self.resolution_label)
        control_layout.addWidget(self.resolution)

        self._clear_existing_layers = QCheckBox("Clear existing layers")
        self._clear_existing_layers.setChecked(True)

        layout = QVBoxLayout()
        layout.addLayout(control_layout)
        layout.addWidget(self._clear_existing_layers)
        layout.addWidget(self._progress)
        self.setLayout(layout)

    def setUri(self, uri: str) -> None:
        """Sets the URI of the portal that should be used to open data."""
        self._uri = uri

    def setTomogram(self, tomogram: Tomogram) -> None:
        """Sets the current tomogram that should be opened."""
        self.cancel()
        self._tomogram = tomogram
        # Reset resolution to low to handle case when user tries
        # out a higher resolution but then moves onto another tomogram.
        self.resolution.setCurrentText(LOW_RESOLUTION.name)
        self.setTitle(f"Tomogram: {tomogram.name}")
        self.show()
        self.load()

    def load(self) -> None:
        """Loads the current tomogram at the current resolution."""
        resolution = self.resolution.currentData()
        logger.debug("OpenWidget.load: %s", self._tomogram, resolution)
        if self._clear_existing_layers.isChecked():
            self._viewer.layers.clear()
        self._progress.submit(self._tomogram, resolution)

    def cancel(self) -> None:
        """Cancels the last tomogram load."""
        logger.debug("OpenWidget.cancel")
        self._progress.cancel()

    def _loadTomogram(
        self,
        tomogram: Tomogram,
        resolution: Resolution,
    ) -> Generator[FullLayerData, None, None]:
        logger.debug("OpenWidget._loadTomogram: %s", tomogram.name)
        image_data, image_attrs, _ = read_tomogram(tomogram)
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
        image_translate = image_attrs.get("translate", (0,) * len(image_attrs["scale"]))
        image_attrs["translate"] = tuple(
            resolution.offset + t for t in image_translate
        )
        yield image_data, image_attrs, "image"

        # Looking up tomogram.tomogram_voxel_spacing.annotations triggers a query
        # using the client from where the tomogram was found.
        # A single client is not thread safe, so we need a new instance for each query.
        client = Client(self._uri)
        annotations = Annotation.find(
            client, 
            [Annotation.tomogram_voxel_spacing_id == tomogram.tomogram_voxel_spacing_id],
        )

        for annotation in annotations:
            point_paths = tuple(
                f.https_path
                for f in annotation.files
                if f.shape_type == "Point"
            )
            if len(point_paths) > 0:
                yield read_annotation(annotation, tomogram=tomogram)
            else:
                logger.warn("Found no points annotations. Skipping.")

    def _onLayerLoaded(self, layer_data: FullLayerData) -> None:
        logger.debug("OpenWidget._onLayerLoaded")
        data, attrs, layer_type = layer_data
        if layer_type == "image":
            self._viewer.add_image(data, **attrs)
        elif layer_type == "points":
            self._viewer.add_points(data, **attrs)
        else:
            raise AssertionError(f"Unexpected {layer_type=}")
