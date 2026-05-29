from fastapi import APIRouter, HTTPException
from sonda_marte_api.armazenamento import probe_repository as repositorio
from sonda_marte_api.schemas.probe_schemas import LancarSondaEntrada, ListaSondasResposta, MoverSondaEntrada, SondaResposta
from sonda_marte_api.servicos import probe as servico
from sonda_marte_api.servicos.probe import ComandoInvalido, saiuForaDosLimites

router = APIRouter(prefix="/probes", tags=["Sondas"])

@router.post(
    "/",
    response_model=SondaResposta,
    status_code=201,
    summary="Lançar sonda e configurar malha",
)
def lancar_sonda(dados: LancarSondaEntrada) -> SondaResposta:
    # cria a sonda direto usando o dataclass Probe
    nova_sonda = servico.Probe(
        id=repositorio.gera_id(),
        x=0,
        y=0,
        direcao=dados.direction.lower(),
        max_x=dados.x,
        max_y=dados.y,
    )

    repositorio.salva_probe(nova_sonda)

    return SondaResposta(
        id=nova_sonda.id,
        x=nova_sonda.x,
        y=nova_sonda.y,
        direction=nova_sonda.direcao,
    )


@router.post(
    "/{probe_id}/commands",
    response_model=SondaResposta,
    summary="Mover sonda",
)
def mover_sonda(probe_id: str, dados: MoverSondaEntrada) -> SondaResposta:
    sonda = repositorio.busca_probe(probe_id)

    if sonda is None:
        raise HTTPException(status_code=404, detail=f"Sonda '{probe_id}' não encontrada.")

    try:
        # agora usa a função correta do seu service
        sonda = servico.processa_comandos(sonda, dados.commands)
    except ComandoInvalido as erro:
        raise HTTPException(status_code=422, detail=str(erro))
    except saiuForaDosLimites as erro:
        raise HTTPException(status_code=422, detail=str(erro))

    repositorio.salva_probe(sonda)

    return SondaResposta(
        id=sonda.id,
        x=sonda.x,
        y=sonda.y,
        direction=sonda.direcao,
    )


@router.get(
    "/",
    response_model=ListaSondasResposta,
    summary="Ver posição de todas as sondas",
)
def listar_sondas() -> ListaSondasResposta:
    sondas = repositorio.lista_probes()

    return ListaSondasResposta(
        probes=[
            SondaResposta(
                id=s.id,
                x=s.x,
                y=s.y,
                direction=s.direcao,
            )
            for s in sondas
        ]
    )