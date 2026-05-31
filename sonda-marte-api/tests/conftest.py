import pytest
from fastapi.testclient import TestClient

from sonda_marte_api.storage import probe_repository as repository
from sonda_marte_api.main import app


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_state_between_tests():
    """Garante que cada teste inicia com o repositório vazio."""
    repository.clear_probes()
    yield
    repository.clear_probes()
