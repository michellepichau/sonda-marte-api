import pytest
from fastapi.testclient import TestClient

from sonda_marte_api.armazenamento import probe_repository as repositorio
from sonda_marte_api import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def limpar_estado_entre_testes():
    """Garante que cada teste começa com o armazenamento vazio."""
    repositorio.limpar_probes()
    yield
    repositorio.limpar_probes()


def lancar_sonda_padrao(**kwargs) -> dict:
    """Atalho para lançar uma sonda com valores padrão nos testes."""
    payload = {"x": 5, "y": 5, "direction": "NORTH", **kwargs}
    return client.post("/probes/", json=payload).json()



class TestLancarSonda:
    def test_retorna201(self):
        resposta = client.post("/probes/", json={"x": 5, "y": 5, "direction": "NORTH"})
        assert resposta.status_code == 201

    def test_sonda_posicao_zero(self):
        sonda = lancar_sonda_padrao()
        assert sonda["x"] == 0
        assert sonda["y"] == 0

    def test_sonda_id_unico(self):
        sonda_1 = lancar_sonda_padrao()
        sonda_2 = lancar_sonda_padrao()
        assert sonda_1["id"] != sonda_2["id"]

    def test_sonda_direcao_inicial(self):
        sonda = lancar_sonda_padrao(direction="EAST")
        assert sonda["direction"] == "EAST"

    def test_rejeita_malha(self):
        resposta = client.post("/probes/", json={"x": 0, "y": 5, "direction": "NORTH"})
        assert resposta.status_code == 422

    def test_rejeita_direcao_invalida(self):
        resposta = client.post("/probes/", json={"x": 5, "y": 5, "direction": "NORDESTE"})
        assert resposta.status_code == 422


class TestMoverSonda:
    def test_sequencia(self):
        """Caso do enunciado: MRM partindo de (0,0,NORTH) → (1,1,EAST)."""
        sonda = lancar_sonda_padrao(direction="NORTH")
        resposta = client.post(f"/probes/{sonda['id']}/commands", json={"commands": "MRM"})

        assert resposta.status_code == 200
        assert resposta.json() == {
            "id": sonda["id"],
            "x": 1,
            "y": 1,
            "direction": "EAST",
        }

    def test_aceita_comandos_minusculo(self):
        sonda = lancar_sonda_padrao(direction="NORTH")
        resposta = client.post(f"/probes/{sonda['id']}/commands", json={"commands": "mrm"})
        assert resposta.status_code == 200
        assert resposta.json()["x"] == 1

    def test_retorna404_sonda_inexistente(self):
        resposta = client.post("/probes/id-que-nao-existe/commands", json={"commands": "M"})
        assert resposta.status_code == 404

    def test_retorna422_comando_invalido(self):
        sonda = lancar_sonda_padrao()
        resposta = client.post(f"/probes/{sonda['id']}/commands", json={"commands": "MXM"})
        assert resposta.status_code == 422

    def test_retorna_422(self):
        sonda = lancar_sonda_padrao(direction="SOUTH")
        resposta = client.post(f"/probes/{sonda['id']}/commands", json={"commands": "M"})
        assert resposta.status_code == 422

    def test_sonda_nao_move_sequencia_invalida(self):
        sonda = lancar_sonda_padrao(direction="NORTH")

        client.post(f"/probes/{sonda['id']}/commands", json={"commands": "MMMMMMMM"})

        resposta = client.get("/probes/")
        sonda_atualizada = next(p for p in resposta.json()["probes"] if p["id"] == sonda["id"])

        assert sonda_atualizada["x"] == 0
        assert sonda_atualizada["y"] == 0

    def test_posicao_persiste(self):
        sonda = lancar_sonda_padrao(direction="NORTH")
        client.post(f"/probes/{sonda['id']}/commands", json={"commands": "MM"})
        client.post(f"/probes/{sonda['id']}/commands", json={"commands": "MM"})

        resposta = client.get("/probes/")
        sonda_atualizada = next(p for p in resposta.json()["probes"] if p["id"] == sonda["id"])
        assert sonda_atualizada["y"] == 4


class TestListarSondas:
    def test_lista_vazia(self):
        resposta = client.get("/probes/")
        assert resposta.status_code == 200
        assert resposta.json() == {"probes": []}

    def test_retorna_todas_sondas(self):
        lancar_sonda_padrao()
        lancar_sonda_padrao()

        resposta = client.get("/probes/")
        assert len(resposta.json()["probes"]) == 2

    def test_retorna_posicao_atualizada(self):
        sonda = lancar_sonda_padrao(direction="NORTH")
        client.post(f"/probes/{sonda['id']}/commands", json={"commands": "MMM"})

        resposta = client.get("/probes/")
        sonda_atualizada = next(p for p in resposta.json()["probes"] if p["id"] == sonda["id"])
        assert sonda_atualizada["y"] == 3