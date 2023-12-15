from napari.components import ViewerModel
import pytest
from pytestqt.qtbot import QtBot

from cryoet_data_portal import Tomogram
from napari.layers import Points

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
    widget._viewer.layers.append(Points())
    assert len(widget._viewer.layers) == 1
    assert widget._clear_existing_layers.isChecked()
    
    with qtbot.waitSignal(widget._progress.finished, timeout=30000):
        widget.setTomogram(tomogram)
    
    assert len(widget._viewer.layers) == 3


def test_set_tomogram_adds_layers_to_viewer_without_clearing_existing(widget: OpenWidget, tomogram: Tomogram, qtbot: QtBot):
    assert len(widget._viewer.layers) == 0
    widget._viewer.layers.append(Points())
    assert len(widget._viewer.layers) == 1
    widget._clear_existing_layers.setChecked(False)

    with qtbot.waitSignal(widget._progress.finished, timeout=30000):
        widget.setTomogram(tomogram)

    assert len(widget._viewer.layers) == 4
    