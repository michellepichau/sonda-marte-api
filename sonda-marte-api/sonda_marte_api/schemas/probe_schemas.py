"""
Schemas Pydantic para validar dados de entrada e serialização de saída da API.
"""

from typing import Literal

from pydantic import BaseModel, Field

Direction = Literal["NORTH", "SOUTH", "EAST", "WEST"]


class SendInputProbe(BaseModel):
    x: int = Field(gt=0, description="O limite máximo do eixo X da malha deve ser > 0")
    y: int = Field(gt=0, description="O limite máximo do eixo Y da malha deve ser > 0")
    direction: Direction = Field(description="Direção inicial da sonda")


class MoveProbeInput(BaseModel):
    commands: str = Field(
        min_length=1,
        description="Esses são os comandos para serem dados: L (esquerda), R (direita), M (mover para frente)",
    )


class ProbeResponse(BaseModel):
    id: str
    x: int
    y: int
    direction: Direction


class ProbeListResponse(BaseModel):
    probes: list[ProbeResponse]
