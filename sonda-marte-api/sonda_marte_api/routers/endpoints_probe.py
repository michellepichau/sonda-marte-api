"""
Endpoints REST para gerenciamento das sondas lançadas em Marte.
"""

from fastapi import APIRouter, HTTPException

from sonda_marte_api.storage import probe_repository as repository
from sonda_marte_api.schemas.probe_schemas import (
    MoveProbeInput,
    ProbeListResponse,
    ProbeResponse,
    SendInputProbe,
)
from sonda_marte_api.service.probe import (
    InvalidCommand,
    Probe,
    WentOutOfLimit,
    execute_commands,
)

router = APIRouter(prefix="/probes", tags=["Probes"])


@router.post(
    "/",
    response_model=ProbeResponse,
    status_code=201,
    summary="Lança uma nova sonda e configura os limites da malha",
)
def launch_probe(payload: SendInputProbe) -> ProbeResponse:
    probe = Probe(
        id=repository.generate_id(),
        x=0,
        y=0,
        direction=payload.direction,
        max_x=payload.x,
        max_y=payload.y,
    )
    repository.save_probe(probe)
    return ProbeResponse(id=probe.id, x=probe.x, y=probe.y, direction=probe.direction)


@router.post(
    "/{probe_id}/commands",
    response_model=ProbeResponse,
    summary="Envia uma sequência de comandos para mover a sonda",
)
def move_probe(probe_id: str, payload: MoveProbeInput) -> ProbeResponse:
    probe = repository.find_probe(probe_id)

    if probe is None:
        raise HTTPException(status_code=404, detail=f"A sonda com o id: '{probe_id}' não foi encontrada.")

    try:
        updated_probe = execute_commands(probe, payload.commands)
    except (InvalidCommand, WentOutOfLimit) as error:
        raise HTTPException(status_code=422, detail=str(error))

    repository.save_probe(updated_probe)
    return ProbeResponse(
        id=updated_probe.id,
        x=updated_probe.x,
        y=updated_probe.y,
        direction=updated_probe.direction,
    )


@router.get(
    "/",
    response_model=ProbeListResponse,
    summary="Lista todas as sondas e suas posições atuais",
)
def list_probes() -> ProbeListResponse:
    probes = repository.list_probes()
    return ProbeListResponse(
        probes=[
            ProbeResponse(id=p.id, x=p.x, y=p.y, direction=p.direction)
            for p in probes
        ]
    )
