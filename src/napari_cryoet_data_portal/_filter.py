from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from napari_cryoet_data_portal._logging import logger

@dataclass(frozen=True)
class Filter:
    dataset_id: Optional[int] = None
    spacing_id: Optional[int] = None

    @classmethod
    def from_names(cls, *, dataset: str, spacing: str) -> Filter:
        return cls(
            dataset_id=_name_to_id(dataset),
            spacing_id=_name_to_id(spacing),
        )

def _name_to_id(name: str) -> Optional[int]:
    id: Optional[int] = None
    if len(name) > 0:
        try:
            id = int(name)
        except ValueError:
            # TODO: should we just let this throw?
            logger.error("Failed to parse ID: %s", name)
    return id
