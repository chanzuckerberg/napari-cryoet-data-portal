from typing import Iterable, Tuple

import pytest
from qtpy.QtWidgets import QTreeWidget, QTreeWidgetItem
from pytest_mock import MockerFixture
from pytestqt.qtbot import QtBot

from napari_cryoet_data_portal._listing_widget import ListingWidget


MOCK_S3_URI = 's3://mock-portal'
DATASET_NAMES = ('10000', '10001')
TOMOGRAM_NAMES = {
    '10000': ('TS_026', 'TS_027'),
    '10001': ('TS_0001', 'TS_0002'),
}
ANNOTATION_NAMES = ('ribosome.json', 'fatty-acid-synthase.json')


def mock_list_dir(path: str) -> Tuple[str, ...]:
    if path == f'{MOCK_S3_URI}':
        return DATASET_NAMES
    for dataset in DATASET_NAMES:
        dataset_path = f'{MOCK_S3_URI}/{dataset}'
        if path == dataset_path:
            return TOMOGRAM_NAMES[dataset]
    return ANNOTATION_NAMES        
    

def top_items(tree: QTreeWidget) -> Tuple[QTreeWidgetItem, ...]:
    return tuple(tree.topLevelItem(i) for i in range(tree.topLevelItemCount()))


def child_items(item: QTreeWidgetItem) -> Tuple[QTreeWidgetItem, ...]:
    return tuple(item.child(i) for i in range(item.childCount()))


def items_names(items: Iterable[QTreeWidgetItem]) -> Tuple[str, ...]:
    return tuple(item.text(0) for item in items)


@pytest.fixture()
def widget(qtbot: QtBot) -> ListingWidget:
    widget = ListingWidget()
    qtbot.add_widget(widget)
    return widget


def test_init(qtbot: QtBot):
    widget = ListingWidget()
    qtbot.add_widget(widget)

    assert widget.tree.isVisibleTo(widget)
    assert widget.filter.isVisibleTo(widget)
    assert not widget._progress.isVisibleTo(widget)


def test_load_lists_data(widget: ListingWidget, mocker: MockerFixture, qtbot: QtBot):
    mocker.patch('napari_cryoet_data_portal._listing_widget.list_dir', mock_list_dir)
    mocker.patch('napari_cryoet_data_portal._model.list_dir', mock_list_dir)

    with qtbot.waitSignal(widget._progress.finished):
        widget.load(MOCK_S3_URI)
    
    dataset_items = top_items(widget.tree)
    assert items_names(dataset_items) == tuple(f'{name} (2)' for name in DATASET_NAMES)
    tomogram_items_10000 = child_items(dataset_items[0])
    assert items_names(tomogram_items_10000) == TOMOGRAM_NAMES['10000']
    tomogram_items_10001 = child_items(dataset_items[1])
    assert items_names(tomogram_items_10001) == TOMOGRAM_NAMES['10001'] 
    