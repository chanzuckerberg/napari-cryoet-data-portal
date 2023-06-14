from typing import Any, Dict, Tuple

import numpy as np

from napari_cryoet_data_portal._model import Dataset, Tomogram


MOCK_S3_URI = 's3://mock-portal'


def mock_dataset(
    *,
    name: str,
    tomograms: Tuple[Tomogram, ...],
) -> Dataset:
    path = f"{MOCK_S3_URI}/{name}"
    return Dataset(
        name=name,
        path=path,
        tomograms=tomograms,
    )


def mock_tomogram(
        *,
        dataset_name: str,
        tomogram_name: str,
        voxel_spacing: str,
        annotation_names: Tuple[str, ...]
) -> Tomogram:
    path = f"{MOCK_S3_URI}/{dataset_name}/{tomogram_name}"
    tomogram_path = f"{path}/Tomograms/VoxelSpacing{voxel_spacing}"
    image_path = f"{tomogram_path}/CanonicalTomogram/{tomogram_name}.zarr"
    annotations_path = f"{tomogram_path}/Annotations"
    annotations_paths = tuple(
        f"{annotations_path}/{name}.json"
        for name in annotation_names
    )
    return Tomogram(
        name=tomogram_name,
        path=path,
        tomogram_path=tomogram_path,
        image_path=image_path,
        annotation_paths=annotations_paths,
    )


MOCK_TOMOGRAM_TS_026 = mock_tomogram(
    dataset_name="10000",
    tomogram_name="TS_026",
    voxel_spacing="13.48",
    annotation_names=("ribosome", "fatty-acid-synthase"),
)

MOCK_TOMOGRAM_TS_026_METADATA = {
    'run_name': 'TS_026',
    'voxel_spacing': 13.48,
    'size': {
        'z': 8,
        'y': 8,
        'x': 8,
    }
}

MOCK_TOMOGRAM_TS_026_IMAGE_DATA = [
    np.zeros((8, 8, 8)),
    np.zeros((4, 4, 4)),
    np.zeros((2, 2, 2)),
]

MOCK_TOMOGRAM_TS_026_IMAGE_ATTRS = {
    'name': 'TS_026',
    'scale': (1, 1, 1),
}

MOCK_TOMOGRAM_TS_026_RIBOSOME_DATA = [[0, 0, 0], [2, 2, 2]]
MOCK_TOMOGRAM_TS_026_RIBOSOME_ATTRS = {'name': 'ribosome'}

MOCK_TOMOGRAM_TS_026_FAS_DATA = [[1, 1, 1], [3, 3, 3]]
MOCK_TOMOGRAM_TS_026_FAS_ATTRS = {'name': 'fatty acid synthase'}

MOCK_TOMOGRAM_TS_027 = mock_tomogram(
    dataset_name="10000",
    tomogram_name="TS_027",
    voxel_spacing="13.48",
    annotation_names=("ribosome", "fatty-acid-synthase"),
)

MOCK_DATASET_10000 = mock_dataset(
    name="10000",
    tomograms=(MOCK_TOMOGRAM_TS_026, MOCK_TOMOGRAM_TS_027),
)

MOCK_DATASET_10000_METADATA = {
    'dataset_title': 'mock dataset',
    'authors': [
        {
            'name': 'mock author',
            'ORCID': "0000-1111-2222-3333",
        }
    ],
    'organism': {
        'name': 'mock organism',
    }
}

MOCK_TOMOGRAM_POS_128 = mock_tomogram(
    dataset_name="10004",
    tomogram_name="Position_128_2",
    voxel_spacing="7.56",
    annotation_names=("ribosome"),
)

MOCK_TOMOGRAM_POS_129 = mock_tomogram(
    dataset_name="10004",
    tomogram_name="Position_129_2",
    voxel_spacing="7.56",
    annotation_names=("ribosome"),
)

MOCK_DATASET_10004 = mock_dataset(
    name="10004",
    tomograms=(MOCK_TOMOGRAM_POS_128, MOCK_TOMOGRAM_POS_129),
)

MOCK_DATASETS = (MOCK_DATASET_10000, MOCK_DATASET_10004)


def mock_path_exists(path: str) -> bool:
    return path == MOCK_S3_URI


def mock_list_dir(path: str) -> Tuple[str, ...]:
    if path == f'{MOCK_S3_URI}':
        return tuple(ds.name for ds in MOCK_DATASETS)
    for ds in MOCK_DATASETS:
        if ds.path == path:
            return tuple(tomo.name for tomo in ds.tomograms)
        for tomo in ds.tomograms:
            if tomo.annotations_path == path:
                return tuple(
                    p.split('/')[-1]
                    for p in tomo.annotation_paths
                )
    raise ValueError(f"Mock path not supported: {path}")


def mock_read_json(path: str) -> Dict[str, Any]:
    if path == MOCK_DATASET_10000.metadata_path:
        return MOCK_DATASET_10000_METADATA
    if path == MOCK_TOMOGRAM_TS_026.tomogram_metadata_path:
        return MOCK_TOMOGRAM_TS_026_METADATA
    raise ValueError(f'Mock path not supported: {path}')


def mock_read_tomogram_ome_zarr(path: str) -> Dict[str, Any]:
    if path == MOCK_TOMOGRAM_TS_026.image_path:
        return MOCK_TOMOGRAM_TS_026_IMAGE_DATA, MOCK_TOMOGRAM_TS_026_IMAGE_ATTRS, "image"
    raise ValueError(f'Mock path not supported: {path}')


def mock_read_points_annotations_json(path: str) -> Dict[str, Any]:
    if path == MOCK_TOMOGRAM_TS_026.annotation_paths[0]:
        return MOCK_TOMOGRAM_TS_026_RIBOSOME_DATA, MOCK_TOMOGRAM_TS_026_RIBOSOME_ATTRS, "points"
    if path == MOCK_TOMOGRAM_TS_026.annotation_paths[1]:
        return MOCK_TOMOGRAM_TS_026_FAS_DATA, MOCK_TOMOGRAM_TS_026_FAS_ATTRS, "points"
    raise ValueError(f'Mock path not supported: {path}')
