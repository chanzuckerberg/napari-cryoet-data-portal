from dataclasses import dataclass
from functools import cache
from typing import TYPE_CHECKING, Generator, Optional, Tuple

import numpy as np
from cryoet_data_portal import Annotation, Client, Tomogram
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

from napari_cryoet_data_portal._logging import logger
from napari_cryoet_data_portal._progress_widget import ProgressWidget
from napari_cryoet_data_portal._reader import (
    read_annotation_files,
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
        image_layer = read_tomogram(tomogram)
        # Extract image_scale before the resolution is taken into account,
        # so we can use it to align other annotations later.
        image_scale = image_layer[1]["scale"]
        yield _handle_image_at_resolution(image_layer, resolution)

        # Looking up tomogram.tomogram_voxel_spacing.annotations triggers a query
        # using the client from where the tomogram was found.
        # A single client is not thread safe, so we need a new instance for each query.
        client = Client(self._uri)
        annotations = Annotation.find(
            client,
            [
                Annotation.tomogram_voxel_spacing_id
                == tomogram.tomogram_voxel_spacing_id
            ],
        )

        for annotation in annotations:
            for layer in read_annotation_files(annotation, tomogram=tomogram):
                if layer[2] == "labels":
                    layer = _handle_image_at_resolution(layer, resolution)
                elif layer[2] == "points":
                    layer = _handle_points_at_scale(layer, image_scale)
                yield layer

    def _onLayerLoaded(self, layer_data: FullLayerData) -> None:
        logger.debug("OpenWidget._onLayerLoaded")
        data, attrs, layer_type = layer_data
        if layer_type == "image":
            self._viewer.add_image(data, **attrs)
        elif layer_type == "points":
            self._viewer.add_points(data, **attrs)
        elif layer_type == "labels":
            self._viewer.add_labels(data, **attrs)
        else:
            raise AssertionError(f"Unexpected {layer_type=}")


def _handle_image_at_resolution(
    layer_data: FullLayerData, resolution: Resolution
) -> FullLayerData:
    data, attrs, layer_type = layer_data
    # Skip indexing for multi-resolution to avoid adding any
    # unnecessary nodes to the dask compute graph.
    if resolution is not MULTI_RESOLUTION:
        data = data[resolution.indices[0]]

    # Materialize low resolution immediately on this thread to prevent napari blocking.
    # Once async loading is working on a stable napari release, we could remove this.
    if resolution is LOW_RESOLUTION:
        data = np.asarray(data)

    # Adjust the scale and and translation based on the resolution.
    image_scale = attrs["scale"]
    attrs["scale"] = tuple(resolution.scale * s for s in image_scale)
    # Offset the translation due to a larger first pixel for lower resolutions.
    # When visualized in napari, this ensures that the different multi-scale
    # layers opened separately share the same visual extent in the canvas that
    # starts at some scaled version of (-0.5, -0.5, -0.5).
    image_translate = attrs.get("translate", (0,) * len(image_scale))
    attrs["translate"] = tuple(
        (s * (resolution.scale - 1) / 2) + t
        for s, t in zip(image_scale, image_translate)
    )
    return data, attrs, layer_type


def _handle_points_at_scale(
    layer_data: FullLayerData, image_scale: Tuple[float, float, float]
) -> FullLayerData:
    data, attrs, layer_type = layer_data
    # Inherit scale from full resolution image, so that points are visually
    # aligned with the image.
    attrs["scale"] = image_scale
    # Scaling points also changes the size in some version of napari, so adjust accordingly.
    if _is_napari_version_less_than("0.5"):
        attrs["size"] /= np.mean(image_scale)
    return data, attrs, layer_type


@cache
def _is_napari_version_less_than(version: str) -> bool:
    try:
        import napari
    except ImportError:
        logger.warn("Failed to import napari")
        return False
    try:
        from packaging.version import InvalidVersion, Version
    except ImportError:
        logger.warn("Failed to import packaging")
        return False
    try:
        actual_version = Version(napari.__version__)
    except InvalidVersion:
        logger.warn(
            "Failed to parse actual napari version from %s ",
            napari.__version__,
        )
    try:
        target_version = Version(version)
    except InvalidVersion:
        logger.warn("Failed to parse target napari version from %s", version)
    return actual_version < target_version
