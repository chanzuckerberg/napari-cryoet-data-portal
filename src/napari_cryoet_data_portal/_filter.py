from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple

from napari_cryoet_data_portal._logging import logger


@dataclass(frozen=True)
class Filter:
    dataset_ids: Tuple[int, ...] = ()
    spacing_ids: Tuple[int, ...] = ()

    @classmethod
    def from_csv(cls, *, datasets: str, spacings: str) -> Filter:
        return cls(
            dataset_ids=_csv_to_ids(datasets),
            spacing_ids=_csv_to_ids(spacings),
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
