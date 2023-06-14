import pytest
from pytest_mock import MockerFixture
from pytestqt.qtbot import QtBot

from napari_cryoet_data_portal._uri_widget import UriWidget
from napari_cryoet_data_portal._tests.utils import (
    MOCK_S3_URI,
    mock_path_exists,
)


@pytest.fixture()
def widget(qtbot: QtBot) -> UriWidget:
    widget = UriWidget()
    qtbot.add_widget(widget)
    return widget


def test_init(qtbot: QtBot):
    widget = UriWidget()
    qtbot.add_widget(widget)

    assert widget._connect_button.isVisibleTo(widget)
    assert widget._choose_dir_button.isVisibleTo(widget)
    assert widget._uri_edit.isVisibleTo(widget)
    assert not widget._disconnect_button.isVisibleTo(widget)
    assert not widget._progress.isVisibleTo(widget)


def test_click_connect_when_uri_exists(widget: UriWidget, qtbot: QtBot, mocker: MockerFixture):
    mocker.patch(
        'napari_cryoet_data_portal._uri_widget.path_exists',
        mock_path_exists,
    )
    widget._uri_edit.setText(MOCK_S3_URI)

    with qtbot.waitSignal(widget.connected):
        widget._connect_button.click()

    assert not widget._connect_button.isVisibleTo(widget)
    assert not widget._choose_dir_button.isVisibleTo(widget)
    assert widget._uri_edit.isVisibleTo(widget)
    assert widget._uri_edit.isReadOnly()
    assert widget._disconnect_button.isVisibleTo(widget)
    assert not widget._progress.isVisibleTo(widget)


def test_click_connect_when_uri_does_not_exist(widget: UriWidget, qtbot: QtBot, mocker: MockerFixture):
    mocker.patch(
        'napari_cryoet_data_portal._uri_widget.path_exists',
        mock_path_exists,
    )
    widget._uri_edit.setText('s3://mock-bad-uri')

    with qtbot.captureExceptions() as exceptions:
        with qtbot.waitSignal(widget._progress.finished):
            widget._connect_button.click()
        assert len(exceptions) == 1
        assert exceptions[0][0] is ValueError

    assert widget._connect_button.isVisibleTo(widget)
    assert widget._choose_dir_button.isVisibleTo(widget)
    assert widget._uri_edit.isVisibleTo(widget)
    assert not widget._uri_edit.isReadOnly()
    assert not widget._disconnect_button.isVisibleTo(widget)
    assert not widget._progress.isVisibleTo(widget)


def test_click_disconnect(widget: UriWidget, qtbot: QtBot):
    widget._onUriChecked((True, MOCK_S3_URI))

    with qtbot.waitSignal(widget.disconnected):
        widget._disconnect_button.click()

    assert widget._connect_button.isVisibleTo(widget)
    assert widget._choose_dir_button.isVisibleTo(widget)
    assert widget._uri_edit.isVisibleTo(widget)
    assert not widget._uri_edit.isReadOnly()
    assert not widget._disconnect_button.isVisibleTo(widget)
    assert not widget._progress.isVisibleTo(widget)


def test_choose_dir_button_clicked(widget: UriWidget, mocker: MockerFixture):
    mock_dir = '/path/to/test'
    def mock_get_existing_directory(_):
        return mock_dir
    mocker.patch(
        'napari_cryoet_data_portal._uri_widget.QFileDialog.getExistingDirectory',
        mock_get_existing_directory,
    )

    widget._choose_dir_button.click()

    assert widget._uri_edit.text() == mock_dir