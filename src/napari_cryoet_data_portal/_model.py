"""Data model used to abstract the contents and structure of the portal."""

from dataclasses import dataclass, field
from functools import cached_property
from typing import Tuple

from napari_cryoet_data_portal._io import list_dir

PORTAL_S3_URI = "s3://cryoet-data-portal-public"

# TODO: hardcoding these correspondences as a short term fix
# for the recent bucket layout change which avoids an extra listing
# call to s3. Need a long term fix here, which likely uses the main
# Python client.
DATASET_TO_SPACING = {
    '10000': 'VoxelSpacing13.48',
    '10001': 'VoxelSpacing13.48',
    '10004': 'VoxelSpacing7.56',
}
DEFAULT_SPACING = 'VoxelSpacing13.48'


@dataclass(frozen=True)
class Subject:
    """Represents a subject or tomogram within a dataset.

    Attributes
    ----------
    name : str
        The name of the subject (e.g. 'TS_026').
    path : str
        The full directory-like path associated with the subject
        (e.g. 's3://cryoet-data-portal-public/10000/TS_026').
    tomogram_path : str
        The full directory-like path to the tomogram directory that contains the volumes and annotations.
        (e.g. 's3://cryoet-data-portal-public/10000/TS_026/Tomograms/VoxelSpacing13.48').
    image_path : str
        The full directory-like path to the tomogram as an OME-Zarr multi-scale image
        (e.g. 's3://cryoet-data-portal-public/10000/TS_026/Tomograms/VoxelSpacing13.48/CanonicalTomogram/TS_026.zarr').
    annotation_paths : tuple of str
        The full file-like paths to the annotation JSON files.
        (e.g. ['s3://cryoet-data-portal-public/10000/TS_026/Tomograms/VoxelSpacing13.48/Annotations/julia_mahamid-ribosome-1.0.json', ...]).
    """

    name: str
    path: str
    tomogram_path: str
    image_path: str
    annotation_paths: Tuple[str, ...]

    @cached_property
    def tomogram_metadata_path(self) -> str:
        return (
            f"{self.tomogram_path}/CanonicalTomogram/tomogram_metadata.json"
        )

    @classmethod
    def from_dataset_path_and_name(
        cls, dataset_path: str, name: str
    ) -> "Subject":
        path = f"{dataset_path}/{name}"
        dataset_name = dataset_path.split('/')[-1]
        spacing = DATASET_TO_SPACING.get(dataset_name, DEFAULT_SPACING)
        tomogram_path = f"{path}/Tomograms/{spacing}"
        image_path = f"{tomogram_path}/CanonicalTomogram/{name}.zarr"
        annotation_dir = f"{tomogram_path}/Annotations"
        annotation_paths = tuple(
            f"{annotation_dir}/{p}"
            for p in list_dir(annotation_dir)
            if p.endswith(".json")
        )
        return cls(
            name=name,
            path=path,
            tomogram_path=tomogram_path,
            image_path=image_path,
            annotation_paths=annotation_paths,
        )


@dataclass(frozen=True)
class Dataset:
    """Represents an entire dataset of many subjects and their annotations.

    Attributes
    ----------
    name : str
        The name of the dataset (e.g. '10000').
    path : str
        The full directory-like path associated with the dataset
        (e.g. 's3://cryoet-data-portal-public/10000').
    subjects : tuple of subjects
        The subjects within the dataset.
    """

    name: str
    path: str
    subjects: Tuple[Subject, ...] = field(repr=False)

    @cached_property
    def metadata_path(self) -> str:
        return f"{self.path}/dataset_metadata.json"

    @classmethod
    def from_data_path_and_name(cls, data_path: str, name: str) -> "Dataset":
        path = f"{data_path}/{name}"
        subjects = tuple(
            Subject.from_dataset_path_and_name(path, p)
            for p in list_dir(path)
            # TODO: better way to select non-hidden directories.
            if "." not in p
        )
        return Dataset(name=name, path=path, subjects=subjects)
