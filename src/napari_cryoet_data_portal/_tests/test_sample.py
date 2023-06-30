from typing import Callable

from napari import Viewer
from napari.layers import Image, Points

from napari_cryoet_data_portal._sample_data import tomogram_10000_ts_026, tomogram_10000_ts_027


def test_tomogram_10000_ts_026():
    layers = tomogram_10000_ts_026()

    assert len(layers) == 3
    assert layers[0][2] == "image"
    assert layers[1][2] == "points"
    assert layers[2][2] == "points"


def test_tomogram_10000_ts_027():
    layers = tomogram_10000_ts_027()

    assert len(layers) == 3
    assert layers[0][2] == "image"
    assert layers[1][2] == "points"
    assert layers[2][2] == "points"


def test_open_sample(make_napari_viewer: Callable[[], Viewer]):
    viewer = make_napari_viewer()

    layers = viewer.open_sample(plugin="napari-cryoet-data-portal", sample="tomogram-10000-ts-026")

    assert len(layers) == 3
    assert isinstance(layers[0], Image)
    assert isinstance(layers[1], Points)
    assert isinstance(layers[2], Points)
