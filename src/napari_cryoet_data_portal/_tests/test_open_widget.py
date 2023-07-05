from napari.components import ViewerModel
import pytest
from pytestqt.qtbot import QtBot

from cryoet_data_portal import Tomogram

from napari_cryoet_data_portal._open_widget import OpenWidget


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


def test_set_tomogram_adds_layers_to_viewer(widget: OpenWidget, tomogram: Tomogram, qtbot: QtBot):
    assert len(widget._viewer.layers) == 0
    
    with qtbot.waitSignal(widget._progress.finished):
        widget.setTomogram(tomogram)
    
    assert len(widget._viewer.layers) == 3
    