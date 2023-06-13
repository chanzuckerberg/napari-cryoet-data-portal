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
    assert widget._disconnect_button.isVisibleTo(widget)
    assert not widget._progress.isVisibleTo(widget)
