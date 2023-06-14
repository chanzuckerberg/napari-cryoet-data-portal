from napari.components import ViewerModel
import pytest
from pytest_mock import MockerFixture
from pytestqt.qtbot import QtBot

from napari_cryoet_data_portal._open_widget import OpenWidget
from napari_cryoet_data_portal._tests.utils import (
    MOCK_TOMOGRAM_TS_026,
    mock_read_points_annotations_json,
    mock_read_tomogram_ome_zarr,
)


@pytest.fixture()
def viewer_model() -> ViewerModel:
    return ViewerModel()


@pytest.fixture()
def widget(viewer_model: ViewerModel, qtbot: QtBot) -> OpenWidget:
    widget = OpenWidget(viewer_model)
    qtbot.add_widget(widget)
    return widget


def test_init(viewer_model: ViewerModel, qtbot: QtBot):
    widget = OpenWidget(viewer_model)
    qtbot.add_widget(widget)

    assert not widget._progress.isVisibleTo(widget)


def test_set_tomogram_adds_layers_to_viewer(widget: OpenWidget, mocker: MockerFixture, qtbot: QtBot):
    mocker.patch('napari_cryoet_data_portal._open_widget.read_tomogram_ome_zarr', mock_read_tomogram_ome_zarr)
    mocker.patch('napari_cryoet_data_portal._open_widget.read_points_annotations_json', mock_read_points_annotations_json)
    assert len(widget._viewer.layers) == 0
    
    with qtbot.waitSignal(widget._progress.finished):
        widget.setTomogram(MOCK_TOMOGRAM_TS_026)
    
    assert len(widget._viewer.layers) == 3
    