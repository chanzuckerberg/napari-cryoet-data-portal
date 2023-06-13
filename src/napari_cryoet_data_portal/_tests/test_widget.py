from typing import Callable

import pytest
from napari import Viewer
from napari.components import ViewerModel
from pytest_mock import MockerFixture
from pytestqt.qtbot import QtBot

from napari_cryoet_data_portal import DataPortalWidget


@pytest.fixture()
def widget(qtbot):
    viewer = ViewerModel()
    widget = DataPortalWidget(viewer)
    qtbot.add_widget(widget)
    return widget


def test_init(qtbot: QtBot):
    viewer = ViewerModel()
    widget = DataPortalWidget(viewer)
    qtbot.add_widget(widget)

    assert widget._uri.isVisibleTo(widget)
    assert not widget._listing.isVisibleTo(widget)
    assert not widget._metadata.isVisibleTo(widget)
    assert not widget._open.isVisibleTo(widget)


def test_add_widget_to_napari(make_napari_viewer: Callable[[], Viewer]):
    viewer = make_napari_viewer()
    _, widget = viewer.window.add_plugin_dock_widget(
        "napari-cryoet-data-portal"
    )
    assert isinstance(widget, DataPortalWidget)


def test_connected_loads_listing(widget: DataPortalWidget, mocker: MockerFixture):
    mocker.patch.object(widget._listing, 'load')
    uri = 's3://mock-portal'

    widget._uri.connected.emit(uri)

    widget._listing.load.assert_called_once_with(uri)
