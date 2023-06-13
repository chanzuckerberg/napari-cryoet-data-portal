from typing import Any, Dict

from napari.components import ViewerModel
import numpy as np
import pytest
from pytest_mock import MockerFixture
from pytestqt.qtbot import QtBot

from napari_cryoet_data_portal._open_widget import OpenWidget
from napari_cryoet_data_portal._model import Subject


MOCK_S3_URI = 's3://mock-portal'
MOCK_IMAGE_DATA = [np.zeros((8, 8, 8)), np.zeros((4, 4, 4)), np.zeros((2, 2, 2))]
MOCK_IMAGE_METADATA = {'name': 'mock image', 'scale': (1, 1, 1)}
MOCK_RIBOSOME_DATA = [[0, 0, 0], [2, 2, 2]]
MOCK_RIBOSOME_METADATA = {'name': 'ribosome'}
MOCK_FAS_DATA = [[1, 1, 1], [3, 3, 3]]
MOCK_FAS_METADATA = {'name': 'fatty acid synthase'}


def mock_read_tomogram_ome_zarr(path: str) -> Dict[str, Any]:
    if path.startswith(MOCK_S3_URI):
        if 'zarr' in path:
            return MOCK_IMAGE_DATA, MOCK_IMAGE_METADATA, "image"
    raise ValueError(f'Mock path not supported: {path}')


def mock_read_points_annotations_json(path: str) -> Dict[str, Any]:
    if path.startswith(MOCK_S3_URI):
        if 'ribosome.json' in path:
            return MOCK_RIBOSOME_DATA, MOCK_RIBOSOME_METADATA, "points"
        if 'fatty-acid-synthase.json' in path:
            return MOCK_FAS_DATA, MOCK_FAS_METADATA, "points"
    raise ValueError(f'Mock path not supported: {path}')


@pytest.fixture()
def viewer_model() -> ViewerModel:
    return ViewerModel()


@pytest.fixture()
def widget(viewer_model: ViewerModel, qtbot: QtBot) -> OpenWidget:
    widget = OpenWidget(viewer_model)
    qtbot.add_widget(widget)
    return widget


@pytest.fixture()
def subject() -> Subject:
    subject_path = f'{MOCK_S3_URI}/10000/TS_026'
    tomogram_path = f'{subject_path}/Tomograms/VoxelSpacing13.48'
    annotations_path = f'{tomogram_path}/Annotations'
    annotations_paths = (
        f'{annotations_path}/ribosome.json',
        f'{annotations_path}/fatty-acid-synthase.json',
    )
    return Subject(
        name='TS_026',
        path=subject_path,
        tomogram_path=tomogram_path,
        image_path=f'{tomogram_path}/TS_026.zarr',
        annotation_paths=annotations_paths,
    )


def test_init(viewer_model: ViewerModel, qtbot: QtBot):
    widget = OpenWidget(viewer_model)
    qtbot.add_widget(widget)

    assert not widget._progress.isVisibleTo(widget)


def test_set_subject_loads_then_adds_layers_to_viewer(widget: OpenWidget, subject: Subject, mocker: MockerFixture, qtbot: QtBot):
    mocker.patch('napari_cryoet_data_portal._open_widget.read_tomogram_ome_zarr', mock_read_tomogram_ome_zarr)
    mocker.patch('napari_cryoet_data_portal._open_widget.read_points_annotations_json', mock_read_points_annotations_json)
    assert len(widget._viewer.layers) == 0
    
    with qtbot.waitSignal(widget._progress.finished):
        widget.setSubject(subject)
    
    assert len(widget._viewer.layers) == 3
    