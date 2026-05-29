# Modelos para a API do Sonda Marte, como entrada/saida de dados, validação, etc.

from typing import Literal
from pydantic import BaseModel, Field



Direction = Literal["NORTH", "SOUTH", "EAST", "WEST"]


class LancarSondaEntrada(BaseModel):
    x: int = Field(gt=0, description="Limite máximo do eixo X da malha")
    y: int = Field(gt=0, description="Limite máximo do eixo Y da malha")
    direction: Direction = Field(description="Direção inicial da sonda")


class MoverSondaEntrada(BaseModel):
    commands: str = Field(
        min_length=1,
        description="Sequência de comandos: L (esquerda), R (direita), M (mover)"
    )


class SondaResposta(BaseModel):
    id: str
    x: int
    y: int
    direction: Direction


class ListaSondasResposta(BaseModel):
    probes: list[SondaResposta]