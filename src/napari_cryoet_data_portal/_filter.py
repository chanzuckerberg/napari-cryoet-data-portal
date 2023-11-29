from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Tuple, Type, Union

from cryoet_data_portal import Dataset, TomogramVoxelSpacing

from napari_cryoet_data_portal._logging import logger

# Guard with type checking because this is a private import.
if TYPE_CHECKING:
    from cryoet_data_portal._gql_base import GQLExpression


@dataclass(frozen=True)
class Filter:
    type: Union[Type[Dataset], Type[TomogramVoxelSpacing]] = Dataset
    ids: Tuple[int, ...] = ()

    def to_gql(self) -> Tuple["GQLExpression", ...]:
        return () if len(self.ids) == 0 else (self.type.id._in(self.ids),)

    @classmethod
    def from_csv(cls, type, *, csv: str) -> Filter:
        return cls(
            type=type,
            ids=_csv_to_ids(csv),
        )


def _csv_to_ids(csv: str) -> Tuple[int, ...]:
    ids: Tuple[int, ...] = ()
    csv = csv.strip()
    if len(csv) > 0:
        try:
            names = csv.split(",")
            ids = tuple(int(name) for name in names)
        except ValueError as e:
            raise ValueError(f"Failed to parse numeric IDs: {csv}") from e
    return ids
