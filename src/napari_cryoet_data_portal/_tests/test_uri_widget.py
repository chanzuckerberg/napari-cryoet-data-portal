import pytest
from pytestqt.qtbot import QtBot

from napari_cryoet_data_portal._filter import DatasetFilter
from napari_cryoet_data_portal._uri_widget import GRAPHQL_URI, UriWidget


@pytest.fixture()
def widget(qtbot: QtBot) -> UriWidget:
    widget = UriWidget()
    qtbot.add_widget(widget)
    return widget


def test_init(qtbot: QtBot):
    widget = UriWidget()
    qtbot.add_widget(widget)

    assert widget._connect_button.isVisibleTo(widget)
    assert widget._uri_edit.isVisibleTo(widget)
    assert not widget._disconnect_button.isVisibleTo(widget)
    assert not widget._progress.isVisibleTo(widget)


def test_click_connect_when_uri_exists(widget: UriWidget, qtbot: QtBot):
    widget._uri_edit.setText(GRAPHQL_URI)

    with qtbot.waitSignal(widget.connected):
        widget._connect_button.click()

    assert not widget._connect_button.isVisibleTo(widget)
    assert widget._uri_edit.isVisibleTo(widget)
    assert widget._disconnect_button.isVisibleTo(widget)
    assert not widget._progress.isVisibleTo(widget)


@pytest.mark.skip(reason="https://github.com/chanzuckerberg/cryoet-data-portal/issues/16")
def test_click_connect_when_uri_does_not_exist(widget: UriWidget, qtbot: QtBot):
    widget._uri_edit.setText("https://not.a.graphl.url/v1/graphql")

    with qtbot.captureExceptions() as exceptions:
        with qtbot.waitSignal(widget._progress.finished):
            widget._connect_button.click()
        assert len(exceptions) == 1
        assert exceptions[0][0] is ValueError

    assert widget._connect_button.isVisibleTo(widget)
    assert widget._uri_edit.isVisibleTo(widget)
    assert not widget._disconnect_button.isVisibleTo(widget)
    assert not widget._progress.isVisibleTo(widget)


def test_click_disconnect(widget: UriWidget, qtbot: QtBot):
    widget._onConnected((GRAPHQL_URI, DatasetFilter()))

    with qtbot.waitSignal(widget.disconnected):
        widget._disconnect_button.click()

    assert widget._connect_button.isVisibleTo(widget)
    assert widget._uri_edit.isVisibleTo(widget)
    assert not widget._disconnect_button.isVisibleTo(widget)
    assert not widget._progress.isVisibleTo(widget)