import pytest

from cryoet_data_portal import Annotation, AnnotationFile, Client, Dataset, Tomogram


@pytest.fixture()
def client() -> Client:
    return Client()


@pytest.fixture()
def dataset(client: Client) -> Dataset:
    return Dataset.find(client, [Dataset.id == 10000]).pop()


@pytest.fixture()
def tomogram(client: Client) -> Tomogram:
    return Tomogram.find(
        client,
        [
            Tomogram.name == "TS_026",
            Tomogram.https_omezarr_dir.like("%13.480%"),
        ],
    ).pop()


@pytest.fixture()
def annotation_with_points(client: Client) -> Annotation:
    anno_file = AnnotationFile.find(client, [AnnotationFile.shape_type == "Point"]).pop()
    return anno_file.annotation
