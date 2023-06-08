from napari_cryoet_data_portal._model import PORTAL_S3_URI, Dataset, Subject


def test_dataset_from_data_path_and_name():
    dataset = Dataset.from_data_path_and_name(PORTAL_S3_URI, "10000")

    assert dataset.name == "10000"
    assert dataset.path == f"{PORTAL_S3_URI}/10000"
    assert len(dataset.subjects) > 0
    subject_names = tuple(s.name for s in dataset.subjects)
    assert "TS_026" in subject_names


def test_subject_from_dataset_path_and_name():
    dataset_dir = f"{PORTAL_S3_URI}/10000"

    subject = Subject.from_dataset_path_and_name(dataset_dir, "TS_026")

    assert subject.name == "TS_026"
    assert subject.path == f"{dataset_dir}/TS_026"
    assert (
        subject.image_path
        == f"{dataset_dir}/TS_026/Tomograms/VoxelSpacing13.48/CanonicalTomogram/TS_026.zarr"
    )
    assert len(subject.annotation_paths) > 0
