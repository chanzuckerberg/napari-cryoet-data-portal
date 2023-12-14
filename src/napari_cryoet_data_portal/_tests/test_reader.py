from typing import Callable

from napari import Viewer
from napari.layers import Points

from napari_cryoet_data_portal import (
    read_points_annotations_ndjson,
    read_tomogram_ome_zarr,
)

CLOUDFRONT_URI = "https://files.cryoetdataportal.cziscience.com"
TOMOGRAM_DIR = f"{CLOUDFRONT_URI}/10000/TS_026/Tomograms/VoxelSpacing13.480"
ANNOTATION_FILE = f"{TOMOGRAM_DIR}/Annotations/101-cytosolic_ribosome-1.0_point.ndjson"


def test_read_tomogram_ome_zarr():
    uri = f"{TOMOGRAM_DIR}/CanonicalTomogram/TS_026.zarr"

    data, attrs, layer_type = read_tomogram_ome_zarr(uri)

    assert len(data) == 3
    assert data[0].shape == (1000, 928, 960)
    assert data[1].shape == (500, 464, 480)
    assert data[2].shape == (250, 232, 240)
    assert attrs["scale"] == (1, 1, 1)
    assert layer_type == "image"


def test_read_points_annotations_ndjson():
    data, attrs, layer_type = read_points_annotations_ndjson(ANNOTATION_FILE)

    assert len(data) == 838
    assert data[0] == (469, 261, 517)
    assert data[418] == (524, 831, 475)
    assert data[837] == (519, 723, 538)
    assert attrs["name"] == "annotations"
    assert layer_type == "points"


def test_open_points_annotations(make_napari_viewer: Callable[[], Viewer]):
    viewer = make_napari_viewer()

    layers = viewer.open(ANNOTATION_FILE, plugin="napari-cryoet-data-portal")

    assert len(layers) == 1
    assert isinstance(layers[0], Points)
