import pytest
from pytestqt.qtbot import QtBot

from napari_cryoet_data_portal._listing_widget import ListingWidget
from napari_cryoet_data_portal._tests._utils import (
    tree_item_children,
    tree_top_items,
)
from napari_cryoet_data_portal._uri_widget import GRAPHQL_URI


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


def test_load_lists_data(widget: ListingWidget, qtbot: QtBot):
    with qtbot.waitSignal(widget._progress.finished, timeout=60000):
        widget.load(GRAPHQL_URI)
    
    dataset_items = tree_top_items(widget.tree)
    assert len(dataset_items) > 0
    tomogram_items = tree_item_children(dataset_items[0])
    assert len(tomogram_items) > 0
    