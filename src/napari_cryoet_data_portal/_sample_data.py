from typing import List

import numpy as np
from npe2.types import FullLayerData
from cryoet_data_portal import Client, Tomogram, TomogramVoxelSpacing

from napari_cryoet_data_portal import (
    read_annotation,
    read_tomogram,
)


def tomogram_10000_ts_026() -> List[FullLayerData]:
    """Returns tomogram TS_026 from dataset 10000 with annotations."""
    return _read_tomogram_from_10000("TS_026")


def tomogram_10000_ts_027() -> List[FullLayerData]:
    """Returns tomogram TS_027 from dataset 10000 with annotations."""
    return _read_tomogram_from_10000("TS_027")


def _read_tomogram_from_10000(name: str) -> List[FullLayerData]:
    client = Client()
    
    tomogram_spacing_url = f"https://files.cryoetdataportal.cziscience.com/10000/{name}/Tomograms/VoxelSpacing13.480/"
    tomogram_spacing = next(TomogramVoxelSpacing.find(client, [TomogramVoxelSpacing.https_prefix == tomogram_spacing_url]))

    tomogram: Tomogram = next(tomogram_spacing.tomograms)

    tomogram_image = read_tomogram(tomogram)
    # Materialize lowest resolution for speed.
    tomogram_image = (np.asarray(tomogram_image[0][-1]), *tomogram_image[1:])
    tomogram_image[1]["scale"] = (4, 4, 4)

    annotations = tuple(tomogram_spacing.annotations)
    ribosome_points = read_annotation(annotations[0], tomogram=tomogram)
    fatty_acid_points = read_annotation(annotations[1], tomogram=tomogram)

    return [
        tomogram_image,
        ribosome_points,
        fatty_acid_points,
    ]
