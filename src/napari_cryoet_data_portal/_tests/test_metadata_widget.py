import pytest
from pytestqt.qtbot import QtBot

from cryoet_data_portal import Dataset, Tomogram

from napari_cryoet_data_portal._metadata_widget import MetadataWidget
from napari_cryoet_data_portal._tests._utils import tree_top_items


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


def test_load_dataset_lists_metadata(widget: MetadataWidget, dataset: Dataset, qtbot: QtBot):
    with qtbot.waitSignal(widget._progress.finished):
        widget.load(dataset)
    
    items = tree_top_items(widget._main.tree)
    assert len(items) > 0

   
def test_load_tomogram_lists_metadata(widget: MetadataWidget, tomogram: Tomogram, qtbot: QtBot):
    with qtbot.waitSignal(widget._progress.finished):
        widget.load(tomogram)
    
    items = tree_top_items(widget._main.tree)
    assert len(items) > 0