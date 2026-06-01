import pytest

from sonda_marte_api.service.probe import (
    InvalidCommand,
    Probe,
    WentOutOfLimit,
    execute_commands,
)


def make_probe(**kwargs) -> Probe:
    """Cria uma sonda com valores padrão, permitindo sobrescrevê-los via kwargs"""
    defaults = {"id": "test-id", "x": 0, "y": 0, "max_x": 5, "max_y": 5, "direction": "NORTH"}
    return Probe(**{**defaults, **kwargs})


class TestProbeCreation:
    def test_starts_at_given_position(self):
        probe = make_probe(x=0, y=0)
        assert probe.x == 0 and probe.y == 0

    def test_stores_initial_direction(self):
        probe = make_probe(direction="EAST")
        assert probe.direction == "EAST"

    def test_stores_grid_limits(self):
        probe = make_probe(max_x=10, max_y=8)
        assert probe.max_x == 10 and probe.max_y == 8


class TestTurnLeft:
    @pytest.mark.parametrize("initial, expected", [
        ("NORTH", "WEST"),
        ("WEST", "SOUTH"),
        ("SOUTH", "EAST"),
        ("EAST", "NORTH"),
    ])
    def test_single_left_turn(self, initial, expected):
        probe = execute_commands(make_probe(direction=initial), "L")
        assert probe.direction == expected

    def test_four_left_turns_returns_to_original(self):
        probe = execute_commands(make_probe(direction="NORTH"), "LLLL")
        assert probe.direction == "NORTH"


class TestTurnRight:
    @pytest.mark.parametrize("initial, expected", [
        ("NORTH", "EAST"),
        ("EAST", "SOUTH"),
        ("SOUTH", "WEST"),
        ("WEST", "NORTH"),
    ])
    def test_single_right_turn(self, initial, expected):
        probe = execute_commands(make_probe(direction=initial), "R")
        assert probe.direction == expected

    def test_four_right_turns_returns_to_original(self):
        probe = execute_commands(make_probe(direction="NORTH"), "RRRR")
        assert probe.direction == "NORTH"


class TestMovement:
    @pytest.mark.parametrize("direction, start_x, start_y, exp_x, exp_y", [
        ("NORTH", 0, 0, 0, 1),
        ("SOUTH", 0, 3, 0, 2),
        ("EAST",  0, 0, 1, 0),
        ("WEST",  3, 0, 2, 0),
    ])
    def test_moves_in_correct_direction(self, direction, start_x, start_y, exp_x, exp_y):
        probe = make_probe(direction=direction)
        probe.x, probe.y = start_x, start_y
        result = execute_commands(probe, "M")
        assert result.x == exp_x and result.y == exp_y


class TestCommandSequence:
    def test_mrm_from_origin_north(self):
        """Caso do enunciado: MRM partindo de (0,0,NORTH) → (1,1,EAST)."""
        probe = execute_commands(make_probe(direction="NORTH"), "MRM")
        assert probe.x == 1 and probe.y == 1 and probe.direction == "EAST"

    def test_rotations_do_not_change_position(self):
        probe = execute_commands(make_probe(direction="NORTH"), "LRLR")
        assert probe.x == 0 and probe.y == 0


class TestBoundaryValidation:
    @pytest.mark.parametrize("direction, start_x, start_y", [
        ("NORTH", 0, 5),
        ("SOUTH", 0, 0),
        ("EAST",  5, 0),
        ("WEST",  0, 0),
    ])
    def test_raises_when_exceeding_boundary(self, direction, start_x, start_y):
        probe = make_probe(direction=direction)
        probe.x, probe.y = start_x, start_y
        with pytest.raises(WentOutOfLimit):
            execute_commands(probe, "M")

    def test_position_unchanged_after_out_of_bounds(self):
        probe = make_probe(direction="NORTH")
        probe.y = 5
        with pytest.raises(WentOutOfLimit):
            execute_commands(probe, "MMMM")
        assert probe.x == 0 and probe.y == 5

    def test_reaches_limit_without_exceeding(self):
        result = execute_commands(make_probe(direction="NORTH"), "MMMMM")
        assert result.y == 5


class TestInvalidCommands:
    def test_raises_on_unknown_character(self):
        with pytest.raises(InvalidCommand):
            execute_commands(make_probe(), "MXM")

    def test_position_unchanged_after_invalid_command(self):
        probe = make_probe(direction="NORTH")
        with pytest.raises(InvalidCommand):
            execute_commands(probe, "MZM")
        assert probe.x == 0 and probe.y == 0

    def test_accepts_lowercase_commands(self):
        result = execute_commands(make_probe(), "m")
        assert result.y == 1