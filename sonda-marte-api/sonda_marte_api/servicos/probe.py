"""
Domínio da sonda: modelo de dados, regras de movimento e validações.
"""

from copy import copy
from dataclasses import dataclass

TURN_RIGHT: dict[str, str] = {
    "NORTH": "EAST",
    "EAST": "SOUTH",
    "SOUTH": "WEST",
    "WEST": "NORTH",
}

TURN_LEFT: dict[str, str] = {
    "NORTH": "WEST",
    "WEST": "SOUTH",
    "SOUTH": "EAST",
    "EAST": "NORTH",
}

MOVEMENT: dict[str, tuple[int, int]] = {
    "NORTH": (0, 1),
    "EAST": (1, 0),
    "SOUTH": (0, -1),
    "WEST": (-1, 0),
}

VALID_COMMANDS = frozenset({"M", "L", "R"})


class WentOutOfLimit(Exception):
    """É acionado quando a sonda tenta se mover para fora dos limites da grade"""


class InvalidCommand(Exception):
    """É acionado quando recebe um caractere de comando não reconhecido"""


@dataclass
class Probe:
    id: str
    x: int
    y: int
    direction: str
    max_x: int
    max_y: int

    def __post_init__(self) -> None:
        self.direction = self.direction.upper()


def execute_command(probe: Probe, command: str) -> Probe:
    """Aplica um único comando à sonda e retorna o estado atualizado"""
    command = command.upper()

    if command not in VALID_COMMANDS:
        raise InvalidCommand(
            f"O comando '{command}' é inválido, esses são os comandos aceitos: {sorted(VALID_COMMANDS)}"
        )

    updated = copy(probe)

    if command == "M":
        dx, dy = MOVEMENT[probe.direction]
        updated.x += dx
        updated.y += dy

        if not (0 <= updated.x <= probe.max_x and 0 <= updated.y <= probe.max_y):
            raise WentOutOfLimit(
                f"A sonda ultrapassaria os limites da malha em ({updated.x}, {updated.y})."
            )

    elif command == "L":
        updated.direction = TURN_LEFT[probe.direction]

    elif command == "R":
        updated.direction = TURN_RIGHT[probe.direction]

    return updated


def execute_commands(probe: Probe, commands: str) -> Probe:
    """Aplica uma sequência de comandos, de forma com que interrompa quando der o primeiro erro."""
    for command in commands:
        probe = execute_command(probe, command)
    return probe
