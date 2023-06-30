import pytest

from cryoet_data_portal import Client, Dataset, Tomogram


@pytest.fixture()
def client() -> Client:
    return Client()


@pytest.fixture()
def dataset(client: Client) -> Dataset:
    return next(Dataset.find(client, [Dataset.id == 10000]))


@pytest.fixture()
def tomogram(client: Client) -> Tomogram:
    return next(Tomogram.find(client, [Tomogram.name == 'TS_026']))