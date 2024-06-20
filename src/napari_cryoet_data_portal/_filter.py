from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, Generator, List, Protocol, Set, Tuple, Type, TypeVar, Union

from cryoet_data_portal import Client, Dataset, Run, Tomogram, TomogramVoxelSpacing

# Guard with type checking because this is a private import.
if TYPE_CHECKING:
    from cryoet_data_portal._gql_base import GQLExpression, GQLField


class Filter(Protocol):
    def load(self, client: Client) -> Generator[Dataset, None, None]:
        """Load the datasets and tomograms that match this filter."""
        ...


@dataclass(frozen=True)
class DatasetFilter:
    ids: Tuple[int, ...] = ()

    def load(self, client: Client) -> Generator[Dataset, None, None]:
        gql_filters = _ids_to_gql(Dataset.id, self.ids)
        yield from Dataset.find(client, gql_filters)


@dataclass(frozen=True)
class RunFilter:
    ids: Tuple[int, ...] = ()

    def load(self, client: Client) -> Generator[Dataset, None, None]:
        datasets: Set[Dataset] = set()
        gql_filters = _ids_to_gql(Run.id, self.ids)
        for run in Run.find(client, gql_filters):
            datasets += run.dataset
        yield from datasets


@dataclass(frozen=True)
class SpacingFilter:
    ids: Tuple[int, ...] = ()

    def load(self, client: Client) -> Generator[Dataset, None, None]:
        datasets: Set[Dataset] = set()
        gql_filters = _ids_to_gql(TomogramVoxelSpacing.id, self.ids)
        for spacing in TomogramVoxelSpacing.find(client, gql_filters):
            datasets += spacing.run.dataset
        yield from datasets

@dataclass(frozen=True)
class TomogramFilter:
    ids: Tuple[int, ...] = ()

    def load(self, client: Client) -> Generator[Dataset, None, None]:
        datasets: Set[Dataset] = set()
        gql_filters = _ids_to_gql(Tomogram.id, self.ids)
        for tomogram in Tomogram.find(client, gql_filters):
            datasets += tomogram.tomogram_voxel_spacing.run.dataset
        yield from datasets


def make_filter(type: Union[Type[Dataset], Type[Run], Type[TomogramVoxelSpacing], Type[Tomogram]], ids: Tuple[int, ...]) -> Filter:
    if type is Dataset:
        return DatasetFilter(ids=ids)
    elif type is Run:
        return RunFilter(ids=ids)
    elif type is TomogramVoxelSpacing:
        return SpacingFilter(ids=ids)
    elif type is Tomogram:
        return TomogramFilter(ids=ids)
    else:
        raise RuntimeError("Entity type not supported: %s", type)


def _ids_to_gql(id_field: "GQLField", ids: Tuple[int, ...]) -> Tuple["GQLExpression", ...]:
    return () if len(ids) == 0 else (id_field._in(ids),)
