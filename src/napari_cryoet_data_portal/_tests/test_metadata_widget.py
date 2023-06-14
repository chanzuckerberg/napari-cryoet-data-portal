from typing import Tuple

import pytest
from qtpy.QtWidgets import QTreeWidget, QTreeWidgetItem
from pytest_mock import MockerFixture
from pytestqt.qtbot import QtBot

from napari_cryoet_data_portal._metadata_widget import MetadataWidget
from napari_cryoet_data_portal._tests._mocks import (
    MOCK_DATASET_10000,
    mock_read_json,
)


def top_items(tree: QTreeWidget) -> Tuple[QTreeWidgetItem, ...]:
    return tuple(tree.topLevelItem(i) for i in range(tree.topLevelItemCount()))


@pytest.fixture()
def widget(qtbot: QtBot) -> MetadataWidget:
    widget = MetadataWidget()
    qtbot.add_widget(widget)
    return widget


def test_init(qtbot: QtBot):
    widget = MetadataWidget()
    qtbot.add_widget(widget)

    assert widget._main.isVisibleTo(widget)
    assert not widget._progress.isVisibleTo(widget)


def test_load_dataset_lists_metadata(widget: MetadataWidget, mocker: MockerFixture, qtbot: QtBot):
    mocker.patch(
        'napari_cryoet_data_portal._metadata_widget.read_json',
        mock_read_json,
    )

    with qtbot.waitSignal(widget._progress.finished):
        widget.load(MOCK_DATASET_10000)
    
    items = top_items(widget._main.tree)
    
    assert len(items) == 3
    assert items[0].text(0) == 'dataset_title'
    assert items[0].text(1) == 'mock dataset'
    assert items[1].text(0) == 'authors'
    assert items[2].text(0) == 'organism'
    