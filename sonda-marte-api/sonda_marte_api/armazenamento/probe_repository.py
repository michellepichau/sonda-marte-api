"""
Repositório em memória para armazenar as sondas durante a execução.
"""

from uuid import uuid4
from sonda_marte_api.servicos.probe import Probe


probes: dict[str, Probe] = {}


def gera_id() -> str:
    return str(uuid4())


def salva_probe(probe: Probe) -> None:
    probes[probe.id] = probe


def busca_probe(probe_id: str) -> Probe | None:
    return probes.get(probe_id)


def lista_probes() -> list[Probe]:
    return list(probes.values())


def limpa_probes() -> None:
    #Limpa todas as sondas. Usado nos testes para isolar o estado.
    probes.clear()