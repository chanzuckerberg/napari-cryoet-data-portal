import pytest
from pytest_mock import MockerFixture
from pytestqt.qtbot import QtBot

from napari_cryoet_data_portal._listing_widget import ListingWidget
from napari_cryoet_data_portal._tests._mocks import (
    MOCK_S3_URI,
    mock_list_dir,
)
from napari_cryoet_data_portal._tests._utils import (
    tree_item_children,
    tree_items_names,
    tree_top_items,
)


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
    mocker.patch(
        'napari_cryoet_data_portal._listing_widget.list_dir',
        mock_list_dir,
    )
    mocker.patch(
        'napari_cryoet_data_portal._model.list_dir',
        mock_list_dir,
    )

    with qtbot.waitSignal(widget._progress.finished):
        widget.load(MOCK_S3_URI)
    
    dataset_items = tree_top_items(widget.tree)
    assert tree_items_names(dataset_items) == ('10000 (2)', '10004 (2)')
    tomogram_items_10000 = tree_item_children(dataset_items[0])
    assert tree_items_names(tomogram_items_10000) == ('TS_026', 'TS_027')
    tomogram_items_10001 = tree_item_children(dataset_items[1])
    assert tree_items_names(tomogram_items_10001) == ('Position_128_2', 'Position_129_2')
    