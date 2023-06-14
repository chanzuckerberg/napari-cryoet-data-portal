from napari_cryoet_data_portal._model import PORTAL_S3_URI, Dataset, Tomogram


def test_dataset_from_data_path_and_name():
    dataset = Dataset.from_data_path_and_name(PORTAL_S3_URI, "10000")

    assert dataset.name == "10000"
    assert dataset.path == f"{PORTAL_S3_URI}/10000"
    assert len(dataset.tomograms) > 0
    tomogram_names = tuple(s.name for s in dataset.tomograms)
    assert "TS_026" in tomogram_names


def test_tomogram_from_dataset_path_and_name():
    dataset_dir = f"{PORTAL_S3_URI}/10000"

    tomogram = Tomogram.from_dataset_path_and_name(dataset_dir, "TS_026")

    assert tomogram.name == "TS_026"
    assert tomogram.path == f"{dataset_dir}/TS_026"
    assert (
        tomogram.image_path
        == f"{dataset_dir}/TS_026/Tomograms/VoxelSpacing13.48/CanonicalTomogram/TS_026.zarr"
    )
    assert len(tomogram.annotation_paths) > 0
