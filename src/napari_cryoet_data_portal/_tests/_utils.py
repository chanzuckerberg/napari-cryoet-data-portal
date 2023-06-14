from typing import Iterable, Tuple

from qtpy.QtWidgets import QTreeWidget, QTreeWidgetItem


def tree_top_items(tree: QTreeWidget) -> Tuple[QTreeWidgetItem, ...]:
    return tuple(tree.topLevelItem(i) for i in range(tree.topLevelItemCount()))


def tree_item_children(item: QTreeWidgetItem) -> Tuple[QTreeWidgetItem, ...]:
    return tuple(item.child(i) for i in range(item.childCount()))


def tree_items_names(items: Iterable[QTreeWidgetItem]) -> Tuple[str, ...]:
    return tuple(item.text(0) for item in items)
