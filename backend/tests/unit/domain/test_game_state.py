import pytest
from app.domain.game_state import GameState, GameWinner, InvalidPhaseError, Phase, Role


@pytest.fixture(autouse=True)
def game_state():
    return GameState()


@pytest.fixture
def night_state(game_state):
    game_state.phase = Phase.NIGHT
    return game_state


@pytest.fixture
def day_state(game_state):
    game_state.phase = Phase.DAY
    return game_state


@pytest.fixture
def voting_state(game_state):
    game_state.phase = Phase.VOTING
    return game_state


def test_add_remove_player(game_state):
    game_state.add_player("p1", {"role": Role.INNOCENT, "alive": True})
    assert game_state.players ==  {"p1": {"role": Role.INNOCENT, "alive": True}}
    game_state.remove_player("p1")
    assert game_state.players == {}


def test_initial_phase_is_night(game_state):
    assert game_state.phase == Phase.NIGHT


def test_end_day_invalid_phase_raises(game_state):
    with pytest.raises(InvalidPhaseError):
        game_state.end_day()


def test_end_day_transitions_to_voting(day_state):
    day_state.end_day()
    assert day_state.phase == Phase.VOTING


def test_end_night_invalid_phase_raises(day_state):
    with pytest.raises(InvalidPhaseError):
        day_state.end_night()


def test_end_night_value_error_raises(night_state):
    with pytest.raises(ValueError):
        night_state.end_night("p1")


def test_end_night_kills_and_transitions_to_day(night_state):
    night_state.add_player("p1", {"role": Role.INNOCENT, "alive": True})
    night_state.add_player("p2", {"role": Role.INNOCENT, "alive": True})
    night_state.add_player("p3", {"role": Role.INNOCENT, "alive": True})
    night_state.add_player("p4", {"role": Role.MAFIA, "alive": True})
    night_state.end_night("p1")
    assert not night_state.players["p1"]["alive"]
    assert night_state.phase == Phase.DAY


def test_end_night_kills_and_transitions_to_ended(night_state):
    night_state.add_player("p1", {"role": Role.INNOCENT, "alive": True})
    night_state.end_night("p1")
    assert not night_state.players["p1"]["alive"]
    assert night_state.phase == Phase.ENDED


def test_end_voting_invalid_phase_raises(day_state):
    with pytest.raises(InvalidPhaseError):
        day_state.end_voting()


def test_end_voting_value_error_raises(voting_state):
    with pytest.raises(ValueError):
        voting_state.end_voting("p1")


def test_end_voting_kills_and_transitions_to_night(voting_state):
    voting_state.add_player("p1", {"role": Role.MAFIA, "alive": True})
    voting_state.add_player("p2", {"role": Role.INNOCENT, "alive": True})
    voting_state.add_player("p3", {"role": Role.INNOCENT, "alive": True})
    voting_state.add_player("p4", {"role": Role.INNOCENT, "alive": True})
    voting_state.end_voting("p2")
    assert not voting_state.players["p2"]["alive"]
    assert voting_state.phase == Phase.NIGHT


def test_end_voting_kills_and_transitions_to_ended(voting_state):
    voting_state.add_player("p1", {"role": Role.MAFIA, "alive": True})
    voting_state.add_player("p2", {"role": Role.INNOCENT, "alive": True})
    voting_state.end_voting("p2")
    assert not voting_state.players["p2"]["alive"]
    assert voting_state.phase == Phase.ENDED


def test_check_game_over_innocents_win(game_state):
    game_state.add_player("i1", {"role": Role.INNOCENT, "alive": True})
    over = game_state.check_game_over()
    assert over
    assert game_state.winner == GameWinner.INNOCENT


def test_check_game_over_mafia_win(game_state):
    game_state.add_player("m1", {"role": Role.MAFIA, "alive": True})
    game_state.add_player("i2", {"role": Role.INNOCENT, "alive": True})
    over = game_state.check_game_over()
    assert over
    assert game_state.winner == GameWinner.MAFIA


def test_check_game_over_draw(game_state):
    over = game_state.check_game_over()
    assert over
    assert game_state.winner == GameWinner.DRAW


def test_check_game_over_continues(game_state):
    game_state.add_player("m1", {"role": Role.MAFIA, "alive": True})
    game_state.add_player("i2", {"role": Role.INNOCENT, "alive": True})
    game_state.add_player("i3", {"role": Role.INNOCENT, "alive": True})
    over = game_state.check_game_over()
    assert not over
    assert game_state.winner is None
