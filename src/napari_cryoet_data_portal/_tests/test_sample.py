from typing import Callable

from napari import Viewer

from napari_cryoet_data_portal._sample_data import tomogram_10000_ts_026, tomogram_10000_ts_027


def test_tomogram_10000_ts_026():
    layers = tomogram_10000_ts_026()
    assert len(layers) == 3


def test_tomogram_10000_ts_027():
    layers = tomogram_10000_ts_027()
    assert len(layers) == 3


def test_open_sample(make_napari_viewer: Callable[[], Viewer]):
    viewer = make_napari_viewer()
    layers = viewer.open_sample(plugin="napari-cryoet-data-portal", sample="tomogram-10000-ts-026")
    assert len(layers) == 3
