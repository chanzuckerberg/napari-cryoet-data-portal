import pytest

from cryoet_data_portal import Annotation, AnnotationFile, Client, Dataset, Tomogram


@pytest.fixture()
def client() -> Client:
    return Client()


@pytest.fixture()
def dataset(client: Client) -> Dataset:
    return next(Dataset.find(client, [Dataset.id == 10000]))


@pytest.fixture()
def tomogram(client: Client) -> Tomogram:
    return next(Tomogram.find(client, [Tomogram.name == 'TS_026', Tomogram.https_omezarr_dir.like("%13.480%")]))


@pytest.fixture()
def annotation_with_points(client: Client) -> Annotation:
    anno_file = next(AnnotationFile.find(client, [AnnotationFile.shape_type == "Point"]))
    return anno_file.annotation