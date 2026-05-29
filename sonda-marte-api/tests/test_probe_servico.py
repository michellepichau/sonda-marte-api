import pytest

from sonda_marte_api.servicos.probe import ComandoInvalido, saiuForaDosLimites, Probe, cria_probe, executa_comandos


def make_probe(**kwargs) -> Probe:
    #cria uma sonda com valores padrão para facilitar os testes.
    defaults = {"id": "test-id", "max_x": 5, "max_y": 5, "direction": "NORTH"}
    return cria_probe(**{**defaults, **kwargs})


class TestCriarProbe:
    def test_comeca_na_posicao_zero(self):
        sonda = make_probe()

        assert sonda.x == 0
        assert sonda.y == 0

    def test_recebe_direcao_inicial(self):
        sonda = make_probe(direction="EAST")

        assert sonda.direction == "EAST"

    def test_limites_da_malha(self):
        sonda = make_probe(max_x=10, max_y=8)

        assert sonda.max_x == 10
        assert sonda.max_y == 8


class TestRotacaoEsquerda:
    def test_norte_vira_oeste(self):
        sonda = make_probe(direction="NORTH")
        executa_comandos(sonda, "L")
        assert sonda.direction == "WEST"

    def test_oeste_vira_sul(self):
        sonda = make_probe(direction="WEST")
        executa_comandos(sonda, "L")
        assert sonda.direction == "SOUTH"

    def test_sul_vira_leste(self):
        sonda = make_probe(direction="SOUTH")
        executa_comandos(sonda, "L")
        assert sonda.direction == "EAST"

    def test_leste_vira_norte(self):
        sonda = make_probe(direction="EAST")
        executa_comandos(sonda, "L")
        assert sonda.direction == "NORTH"

    def test_quatro_rotacoes_direcao_original(self):
        sonda = make_probe(direction="NORTH")
        executa_comandos(sonda, "LLLL")
        assert sonda.direction == "NORTH"


class TestRotacaoDireita:
    def test_norte_vira_leste(self):
        sonda = make_probe(direction="NORTH")
        executa_comandos(sonda, "R")
        assert sonda.direction == "EAST"

    def test_leste_vira_sul(self):
        sonda = make_probe(direction="EAST")
        executa_comandos(sonda, "R")
        assert sonda.direction == "SOUTH"

    def test_sul_vira_oeste(self):
        sonda = make_probe(direction="SOUTH")
        executa_comandos(sonda, "R")
        assert sonda.direction == "WEST"

    def test_oeste_vira_norte(self):
        sonda = make_probe(direction="WEST")
        executa_comandos(sonda, "R")
        assert sonda.direction == "NORTH"

    def test_quatro_rotacoes_direcao_original(self):
        sonda = make_probe(direction="NORTH")
        executa_comandos(sonda, "RRRR")
        assert sonda.direction == "NORTH"



class TestMovimento:
    def test_move_para_norte(self):
        sonda = make_probe(direction="NORTH")
        executa_comandos(sonda, "M")
        assert sonda.x == 0 and sonda.y == 1

    def test_move_para_sul(self):
        sonda = cria_probe(id="t", max_x=5, max_y=5, direction="SOUTH")
        sonda.y = 3
        executa_comandos(sonda, "M")
        assert sonda.x == 0 and sonda.y == 2

    def test_move_para_leste(self):
        sonda = make_probe(direction="EAST")
        executa_comandos(sonda, "M")
        assert sonda.x == 1 and sonda.y == 0

    def test_move_para_oeste(self):
        sonda = cria_probe(id="t", max_x=5, max_y=5, direction="WEST")
        sonda.x = 3
        executa_comandos(sonda, "M")
        assert sonda.x == 2 and sonda.y == 0

class TestSequenciaDeComandos:
    def test_sequencia(self):
        """Caso do enunciado: MRM partindo de (0,0,NORTH) → (1,1,EAST)."""
        sonda = make_probe(direction="NORTH")
        executa_comandos(sonda, "MRM")
        assert sonda.x == 1
        assert sonda.y == 1
        assert sonda.direction == "EAST"

    def test_rotacao_nao_altera_posicao(self):
        sonda = make_probe(direction="NORTH")
        executa_comandos(sonda, "LRLR")
        assert sonda.x == 0
        assert sonda.y == 0


class TestValidacaoDeLimites:
    def test_sonda_nao_sai_pelo_norte(self):
        sonda = cria_probe(id="t", max_x=5, max_y=5, direction="NORTH")
        sonda.y = 5
        with pytest.raises(saiuForaDosLimites):
            executa_comandos(sonda, "M")

    def test_sonda_nao_sai_pelo_sul(self):
        sonda = make_probe(direction="SOUTH")
        with pytest.raises(saiuForaDosLimites):
            executa_comandos(sonda, "M")

    def test_sonda_nao_sai_pelo_leste(self):
        sonda = cria_probe(id="t", max_x=5, max_y=5, direction="EAST")
        sonda.x = 5
        with pytest.raises(saiuForaDosLimites):
            executa_comandos(sonda, "M")

    def test_sonda_nao_sai_pelo_oeste(self):
        sonda = make_probe(direction="WEST")
        with pytest.raises(saiuForaDosLimites):
            executa_comandos(sonda, "M")

    def test_sequencia_invalida(self):
        #Se qualquer comando causar saída dos limites, a sonda não deve se mover.
        sonda = make_probe(direction="NORTH")
        sonda.y = 5

        with pytest.raises(saiuForaDosLimites):
            executa_comandos(sonda, "MMMM")

        assert sonda.x == 0
        assert sonda.y == 5

    def test_sonda_atinge_limites_sem_ultrapassar(self):
        sonda = make_probe(direction="NORTH", max_x=5, max_y=5)
        executa_comandos(sonda, "MMMMM")
        assert sonda.y == 5


class TestComandosInvalidos:
    def test_caractere_invalido(self):
        sonda = make_probe()
        with pytest.raises(ComandoInvalido):
            executa_comandos(sonda, "MXM")

    def test_comando_invalido(self):
        sonda = make_probe(direction="NORTH")
        with pytest.raises(ComandoInvalido):
            executa_comandos(sonda, "MZM")
        assert sonda.x == 0
        assert sonda.y == 0

    def test_aceita_comandos_minusculo(self):
        sonda = make_probe()
        with pytest.raises(ComandoInvalido):
            executa_comandos(sonda, "m")