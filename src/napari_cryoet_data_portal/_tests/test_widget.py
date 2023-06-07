from typing import Callable

from napari import Viewer
from napari.components import ViewerModel
from pytestqt.qtbot import QtBot

from napari_cryoet_data_portal import DataPortalWidget


def test_init_data_portal_widget(qtbot: QtBot):
    viewer = ViewerModel
    widget = DataPortalWidget(viewer)
    qtbot.add_widget(widget)


def test_add_widget_to_napari(make_napari_viewer: Callable[[], Viewer]):
    viewer = make_napari_viewer()
    _, widget = viewer.window.add_plugin_dock_widget(
        "napari-cryoet-data-portal"
    )
    assert isinstance(widget, DataPortalWidget)
