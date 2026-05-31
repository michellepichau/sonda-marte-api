import pytest
from fastapi.testclient import TestClient


def launch_probe(client: TestClient, **kwargs) -> dict:
    """Lança uma sonda com valores padrão, sobrescrevíveis via kwargs."""
    payload = {"x": 5, "y": 5, "direction": "NORTH", **kwargs}
    return client.post("/probes/", json=payload).json()


class TestLaunchProbe:
    def test_returns_201(self, client: TestClient):
        response = client.post("/probes/", json={"x": 5, "y": 5, "direction": "NORTH"})
        assert response.status_code == 201

    def test_probe_starts_at_origin(self, client: TestClient):
        probe = launch_probe(client)
        assert probe["x"] == 0
        assert probe["y"] == 0

    def test_probe_has_unique_id(self, client: TestClient):
        probe_1 = launch_probe(client)
        probe_2 = launch_probe(client)
        assert probe_1["id"] != probe_2["id"]

    def test_probe_initial_direction(self, client: TestClient):
        probe = launch_probe(client, direction="EAST")
        assert probe["direction"] == "EAST"

    def test_rejects_zero_grid_size(self, client: TestClient):
        response = client.post("/probes/", json={"x": 0, "y": 5, "direction": "NORTH"})
        assert response.status_code == 422

    def test_rejects_invalid_direction(self, client: TestClient):
        response = client.post("/probes/", json={"x": 5, "y": 5, "direction": "NORTHEAST"})
        assert response.status_code == 422


class TestMoveProbe:
    def test_command_sequence(self, client: TestClient):
        """Caso do enunciado: MRM partindo de (0,0,NORTH) → (1,1,EAST)."""
        probe = launch_probe(client, direction="NORTH")
        response = client.post(f"/probes/{probe['id']}/commands", json={"commands": "MRM"})

        assert response.status_code == 200
        assert response.json() == {"id": probe["id"], "x": 1, "y": 1, "direction": "EAST"}

    def test_accepts_lowercase_commands(self, client: TestClient):
        probe = launch_probe(client, direction="NORTH")
        response = client.post(f"/probes/{probe['id']}/commands", json={"commands": "mrm"})
        assert response.status_code == 200
        assert response.json()["x"] == 1

    def test_returns_404_for_unknown_probe(self, client: TestClient):
        response = client.post("/probes/nonexistent-id/commands", json={"commands": "M"})
        assert response.status_code == 404

    def test_returns_422_for_invalid_command_character(self, client: TestClient):
        probe = launch_probe(client)
        response = client.post(f"/probes/{probe['id']}/commands", json={"commands": "MXM"})
        assert response.status_code == 422

    def test_returns_422_when_out_of_bounds(self, client: TestClient):
        probe = launch_probe(client, direction="SOUTH")
        response = client.post(f"/probes/{probe['id']}/commands", json={"commands": "M"})
        assert response.status_code == 422

    def test_probe_position_unchanged_after_failed_sequence(self, client: TestClient):
        probe = launch_probe(client, direction="NORTH")
        client.post(f"/probes/{probe['id']}/commands", json={"commands": "MMMMMMMM"})

        updated = next(
            p for p in client.get("/probes/").json()["probes"] if p["id"] == probe["id"]
        )
        assert updated["x"] == 0
        assert updated["y"] == 0

    def test_position_persists_across_commands(self, client: TestClient):
        probe = launch_probe(client, direction="NORTH")
        client.post(f"/probes/{probe['id']}/commands", json={"commands": "MM"})
        client.post(f"/probes/{probe['id']}/commands", json={"commands": "MM"})

        updated = next(
            p for p in client.get("/probes/").json()["probes"] if p["id"] == probe["id"]
        )
        assert updated["y"] == 4


class TestListProbes:
    def test_returns_empty_list_initially(self, client: TestClient):
        response = client.get("/probes/")
        assert response.status_code == 200
        assert response.json() == {"probes": []}

    def test_returns_all_launched_probes(self, client: TestClient):
        launch_probe(client)
        launch_probe(client)
        assert len(client.get("/probes/").json()["probes"]) == 2

    def test_returns_updated_position_after_move(self, client: TestClient):
        probe = launch_probe(client, direction="NORTH")
        client.post(f"/probes/{probe['id']}/commands", json={"commands": "MMM"})

        updated = next(
            p for p in client.get("/probes/").json()["probes"] if p["id"] == probe["id"]
        )
        assert updated["y"] == 3