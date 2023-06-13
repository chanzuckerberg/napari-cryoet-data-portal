from typing import Tuple

import pytest
from pytest_mock import MockerFixture
from pytestqt.qtbot import QtBot

from napari_cryoet_data_portal._uri_widget import UriWidget


MOCK_S3_URI = 's3://mock-portal'
DATASET_NAMES = ('10000', '10001', '10004')
TOMOGRAM_NAMES = ('TS_026', 'TS_027', 'TS_028')


def mock_path_exists(path: str) -> bool:
    return path == MOCK_S3_URI


def mock_list_dir(path: str) -> Tuple[str, ...]:
    if path == f'{MOCK_S3_URI}':
        return DATASET_NAMES
    elif path == f'{MOCK_S3_URI}/10000':
        return TOMOGRAM_NAMES
    raise ValueError('Mock path {path} not supported.')


@pytest.fixture()
def widget(qtbot: QtBot):
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
    mocker.patch('napari_cryoet_data_portal._uri_widget.path_exists', mock_path_exists)
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
    mocker.patch('napari_cryoet_data_portal._uri_widget.path_exists', mock_path_exists)
    widget._uri_edit.setText('s3://mock-bad-uri')

    with qtbot.captureExceptions() as exceptions:
        widget._connect_button.click()
        qtbot.waitUntil(widget._connect_button.isEnabled)
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
    mocker.patch('napari_cryoet_data_portal._uri_widget.QFileDialog.getExistingDirectory', mock_get_existing_directory)

    widget._choose_dir_button.click()

    assert widget._uri_edit.text() == mock_dir