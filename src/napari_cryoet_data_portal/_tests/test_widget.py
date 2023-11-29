from typing import Callable, List, Tuple

import pytest
from cryoet_data_portal import Client
from napari import Viewer
from napari.components import ViewerModel
from pytest_mock import MockerFixture
from pytestqt.qtbot import QtBot
from qtpy.QtWidgets import QWidget

from napari_cryoet_data_portal import DataPortalWidget
from napari_cryoet_data_portal._filter import DatasetFilter
from napari_cryoet_data_portal._uri_widget import GRAPHQL_URI


@pytest.fixture()
def widget(qtbot: QtBot) -> DataPortalWidget:
    viewer = ViewerModel()
    widget = DataPortalWidget(viewer)
    qtbot.add_widget(widget)
    return widget


def show_all_sub_widgets(widget: DataPortalWidget) -> Tuple[QWidget, ...]:
    layout = widget.layout()
    sub_widgets: List[QWidget] = []
    for i in range(layout.count()):
        if w := layout.itemAt(i).widget():
            sub_widgets.append(w)
            w.show()
    return tuple(sub_widgets)


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


def test_listing_item_changed_to_none(widget: DataPortalWidget):
    sub_widgets = show_all_sub_widgets(widget)

    widget._listing.tree.currentItemChanged.emit(None, None)

    assert all(
        w.isVisibleTo(widget) == (w in (widget._uri, widget._listing))
        for w in sub_widgets
    )


def test_connected_loads_listing(widget: DataPortalWidget, mocker: MockerFixture):
    mocker.patch.object(widget._listing, 'load')
    filter = DatasetFilter()

    widget._uri.connected.emit(GRAPHQL_URI, filter)

    widget._listing.load.assert_called_once_with(GRAPHQL_URI, filter=filter)


def test_disconnected_only_shows_uri(widget: DataPortalWidget):
    sub_widgets = show_all_sub_widgets(widget)

    widget._uri.disconnected.emit()

    assert all(
        w.isVisibleTo(widget) == (w is widget._uri)
        for w in sub_widgets
    )