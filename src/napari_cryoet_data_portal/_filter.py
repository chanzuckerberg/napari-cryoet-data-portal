from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, Generator, List, Protocol, Tuple, Type, Union

from cryoet_data_portal import Client, Dataset, Run, Tomogram, TomogramVoxelSpacing

# Guard with type checking because this is a private import.
if TYPE_CHECKING:
    from cryoet_data_portal._gql_base import GQLExpression, GQLField


class Filter(Protocol):
    def load(self, client: Client) -> Generator[Tuple[Dataset, List[Tomogram]], None, None]:
        """Load the datasets and tomograms that match this filter."""
        ...


@dataclass(frozen=True)
class DatasetFilter:
    ids: Tuple[int, ...] = ()

    def load(self, client: Client) -> Generator[Tuple[Dataset, List[Tomogram]], None, None]:
        gql_filters = _ids_to_gql(Dataset.id, self.ids)
        for dataset in Dataset.find(client, gql_filters):
            tomograms: List[Tomogram] = []
            for run in dataset.runs:
                for spacing in run.tomogram_voxel_spacings:
                    tomograms.extend(spacing.tomograms)
            yield dataset, tomograms


@dataclass(frozen=True)
class RunFilter:
    ids: Tuple[int, ...] = ()

    def load(self, client: Client) -> Generator[Tuple[Dataset, List[Tomogram]], None, None]:
        datasets: Dict[int, Dataset] = {}
        tomograms: Dict[int, List[Tomogram]] = defaultdict(list)
        gql_filters = _ids_to_gql(Run.id, self.ids)
        for run in Run.find(client, gql_filters):
            dataset = run.dataset
            datasets[dataset.id] = dataset
            for spacing in run.tomogram_voxel_spacings:
                tomograms[dataset.id].extend(spacing.tomograms)
        for i in datasets:
            yield datasets[i], tomograms[i]


@dataclass(frozen=True)
class SpacingFilter:
    ids: Tuple[int, ...] = ()

    def load(self, client: Client) -> Generator[Tuple[Dataset, List[Tomogram]], None, None]:
        datasets: Dict[int, Dataset] = {}
        tomograms: Dict[int, List[Tomogram]] = defaultdict(list)
        gql_filters = _ids_to_gql(TomogramVoxelSpacing.id, self.ids)
        for spacing in TomogramVoxelSpacing.find(client, gql_filters):
            dataset = spacing.run.dataset
            datasets[dataset.id] = dataset
            tomograms[dataset.id].extend(spacing.tomograms)
        for i in datasets:
            yield datasets[i], tomograms[i]


@dataclass(frozen=True)
class TomogramFilter:
    ids: Tuple[int, ...] = ()

    def load(self, client: Client) -> Generator[Tuple[Dataset, List[Tomogram]], None, None]:
        datasets: Dict[int, Dataset] = {}
        tomograms: Dict[int, List[Tomogram]] = defaultdict(list)
        gql_filters = _ids_to_gql(Tomogram.id, self.ids)
        for tomogram in Tomogram.find(client, gql_filters):
            dataset = tomogram.tomogram_voxel_spacing.run.dataset
            datasets[dataset.id] = dataset
            tomograms[dataset.id].append(tomogram)
        for i in datasets:
            yield datasets[i], tomograms[i]


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
