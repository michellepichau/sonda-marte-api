"""
Implementação de repositório em memória utilizada para persistência 
temporária das sondas durante a execução da aplicação.

Em um ambiente de produção, esta implementação pode ser substituída por um banco de dados, 
mantendo a compatibilidade com a interface pública definida pelo repositório.
"""

from uuid import uuid4

from sonda_marte_api.servicos.probe import Probe

_probes: dict[str, Probe] = {}


def generate_id() -> str:
    return str(uuid4())


def save_probe(probe: Probe) -> None:
    _probes[probe.id] = probe


def find_probe(probe_id: str) -> Probe | None:
    return _probes.get(probe_id)


def list_probes() -> list[Probe]:
    return list(_probes.values())


def clear_probes() -> None:
    """Remove todas as sondas armazenadas, garantindo o isolamento de estado entre os testes"""
    _probes.clear()
