from datetime import datetime, timezone
from app.domain.game_manager import GameManager, PlayerAdapter
from app.domain.game_state import Phase, Role
import pytest
from schemas.game import MessagePayload, MessageReceived, PlayerJoin, PlayerJoinPayload, PlayerLeave, PlayerLeavePayload, SendMessage, Vote, VotePayload


class DummyPlayer(PlayerAdapter):
    def __init__(self):
        self.events = []

    def receive_event(self, event):
        self.events.append(event)


@pytest.fixture
def gm():
    return GameManager()

@pytest.fixture
def dummy_player():
    return DummyPlayer()

@pytest.fixture
def gm_two_players():
    gm = GameManager()
    p1 = DummyPlayer()
    p2 = DummyPlayer()
    gm.add_player('p1', 'Alice', p1)
    gm.add_player('p2', 'Bob', p2)
    return gm, p1, p2


def test_add_remove_player(gm, dummy_player):
    gm.add_player('p1', 'Alice', dummy_player)
    assert 'p1' in gm.players
    assert gm.game_state.players['p1']['alive']
    gm.remove_player('p1')
    assert 'p1' not in gm.players
    assert 'p1' not in gm.game_state.players


def test_get_vote_winner_unique(gm):
    gm.cast_votes = {'a': 'x', 'b': 'x', 'c': 'y'}
    assert gm._get_vote_winner() == 'x'


def test_get_vote_winner_tie_returns_none(gm):
    gm.cast_votes = {'a': 'x', 'b': 'y'}
    assert gm._get_vote_winner() is None


def test_assign_roles_randomly(monkeypatch, gm):
    for uid in ['u1', 'u2', 'u3', 'u4']:
        gm.add_player(uid, uid, DummyPlayer())
    # ensure consistent sampling
    monkeypatch.setattr('app.domain.game_manager.random.sample', lambda lst, k: lst[:k])
    gm._assign_roles_randomly()
    roles = [gm.game_state.players[uid]['role'] for uid in ['u1', 'u2', 'u3', 'u4']]
    assert roles[:2] == [Role.MAFIA, Role.MAFIA]
    assert roles[2:] == [Role.INNOCENT, Role.INNOCENT]


def test_receive_vote_updates_and_ack(gm_two_players):
    gm, p1, p2 = gm_two_players
    gm.game_state.phase = Phase.VOTING
    vote_event = Vote(type="action.vote", payload=VotePayload(actor_id='p1', target_id='p2'))
    gm.receive_event(vote_event, p1)
    assert gm.cast_votes['p1'] == 'p2'
    acks = [e for e in p1.events if getattr(e, 'type', None) == 'action.ack']
    assert acks, "No ack sent to voter"


def test_receive_player_join_and_leave():
    gm = GameManager()
    p = DummyPlayer()
    join = PlayerJoin(type='player.join', payload=PlayerJoinPayload(player_id='p1', name='Alice'))
    gm.receive_event(join, p)
    assert 'p1' in gm.players
    leave = PlayerLeave(type='player.leave', payload=PlayerLeavePayload(player_id='p1'))
    gm.receive_event(leave, p)
    assert 'p1' not in gm.players


def test_send_message_in_lobby_and_day(gm_two_players):
    gm, p1, p2 = gm_two_players
    # lobby: allowed
    msg = SendMessage(
        type='message.send',
        payload=MessagePayload(actor_id='p1', timestamp=datetime.now(timezone.utc), text='hi')
    )

    gm.receive_event(msg, p1)

    received = [e for e in p2.events if isinstance(e, MessageReceived)]
    assert received and received[0].payload.text == 'hi'

    # day: allowed
    p1.events.clear(); p2.events.clear()
    gm.lobby = False
    gm.game_state.phase = Phase.DAY
    msg = SendMessage(
        type='message.send',
        payload=MessagePayload(actor_id='p1', timestamp=datetime.now(timezone.utc), text='hi')
    )

    gm.receive_event(msg, p1)

    received = [e for e in p2.events if isinstance(e, MessageReceived)]
    assert received and received[0].payload.text == 'hi'

    # at night: blocked
    p1.events.clear(); p2.events.clear()
    gm.game_state.phase = Phase.NIGHT

    gm.receive_event(msg, p1)
    ack = [e for e in p1.events if getattr(e, 'type', None) == 'action.ack']

    assert ack
    assert not any(isinstance(e, MessageReceived) for e in p2.events)
