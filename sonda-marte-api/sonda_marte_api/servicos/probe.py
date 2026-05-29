from copy import copy
from dataclasses import dataclass # dessa forma fica mais fácil de criar classes simples e de forma automática

# define pra onde ela vira quando recebe R
gira_direita = {
    "NORTH": "EAST",
    "EAST": "SOUTH",
    "SOUTH": "WEST",
    "WEST": "NORTH",
}

# define pra onde ela vira quando recebe L
gira_esquerda = {
    "NORTH": "WEST",
    "WEST": "SOUTH",
    "SOUTH": "EAST",
    "EAST": "NORTH",
}   

#define onde a posição da sonda muda quando ela recebe M
movimento = {
    "NORTH": (0, 1),
    "EAST": (1, 0),
    "SOUTH": (0, -1),
    "WEST": (-1, 0)
}

comandos_validos = ["M", "L", "R"]


# Erro pra quando sai fora da malha
class saiuForaDosLimites(Exception):
    pass

# Erro para comando inválido
class ComandoInvalido(Exception):
    pass


@dataclass
class Probe:
    id: str
    x: int
    y: int
    direcao: str
    max_x: int
    max_y: int
    
    # padroniza a direção de entrada
    def __post_init__(self):
        self.direcao = self.direcao.upper()
    
# processa um comando e retorna a nova posição da sonda
def processa_comando(sonda: Probe, comando: str) -> Probe:
    comando = comando.upper()
    
    if comando not in comandos_validos: 
        raise ComandoInvalido(f"Comando '{comando}' é inválido. Comandos válidos são: {comandos_validos}")
    
    nova_sonda = copy(sonda)
    
    if comando == "M":
        dx, dy = movimento[sonda.direcao]
        nova_sonda.x += dx
        nova_sonda.y += dy
        
        if nova_sonda.x < 0 or nova_sonda.x > sonda.max_x or nova_sonda.y < 0 or nova_sonda.y > sonda.max_y:
            raise saiuForaDosLimites(f"Sonda saiu dos limites do terreno: ({nova_sonda.x}, {nova_sonda.y})")
    
    elif comando == "L":
        nova_sonda.direcao = gira_esquerda[sonda.direcao]
    
    elif comando == "R":
        nova_sonda.direcao = gira_direita[sonda.direcao]
    
    return nova_sonda

def processa_comandos(sonda: Probe, comandos: str) -> Probe:
    for comando in comandos:
        sonda = processa_comando(sonda, comando)
    return sonda

