from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from schemas.game import (
    ActionAck,
    ActionAckPayload,
    EveningNews,
    EveningNewsPayload,
    GameEvent,
    GameLogEntry,
    GameStateSync,
    GameStateSyncPayload,
    MessageReceived,
    MorningNews,
    MorningNewsPayload,
    NightAction,
    PhaseChange,
    PhaseChangePayload,
    PlayerJoin,
    PlayerJoined,
    PlayerJoinedPayload,
    PlayerLeave,
    PlayerLeft,
    PlayerLeftPayload,
    PlayerState,
    SendMessage,
    Vote,
    VoteCast,
    VoteCastPayload,
)
from app.domain.game_state import GameState, Phase, PlayerGameState, Role


class PlayerAdapter(ABC):
    @abstractmethod
    def receive_event(self, event: GameEvent):
        raise NotImplementedError


class GameManager:
    def __init__(self, night_duration_s=30, day_duration_s=60, vote_duration_s=30):
        self.game_state = GameState()
        self.players: Dict[str, PlayerAdapter] = dict()
        self.player_names: Dict[str, str] = dict()
        self.lobby = True
        self.next_phase_timestamp: datetime = datetime.now(tz=timezone.utc) + timedelta(
            minutes=1, milliseconds=499
        )
        self.night_duration_s = night_duration_s
        self.day_duration_s = day_duration_s
        self.vote_duration_s = vote_duration_s
        # TODO: refactor to map str -> str
        self.cast_votes: Dict[str, int] = defaultdict(int)
        self.event_log: List[GameLogEntry] = []

    def _broadcast(
        self, event: GameEvent, excluded_player_ids=None, included_player_roles=None
    ):
        excluded_player_ids = excluded_player_ids or []
        included_player_roles = included_player_roles or []
        for uuid, player in self.players.items():
            if uuid not in excluded_player_ids and (
                len(included_player_roles) == 0
                or self.game_state.players[uuid]["role"] in included_player_roles
            ):
                player.receive_event(event)

    def add_player(self, uuid: str, name: str, player: PlayerAdapter):
        self.players[uuid] = player
        self.player_names[uuid] = name
        self.game_state.add_player(uuid, PlayerGameState(role=Role.INNOCENT, alive=True))

    def remove_player(self, uuid: str):
        del self.players[uuid]
        del self.player_names[uuid]
        self.game_state.remove_player(uuid)

    def _reset_votes(self):
        self.cast_votes = defaultdict(int, {uuid: 0 for uuid in self.players})
        for uuid in self.players.keys():
            self.cast_votes[uuid] = 0

    def _get_vote_winner(self):
        max_count = max(self.cast_votes.values())
        winners = [k for k, v in self.cast_votes.items() if v == max_count]
        if len(winners) == 1:
            return winners[0]
        else:
            return None

    def _confidentially_reveal_role(self, role: Role, viewer_role: Role):
        if viewer_role == role:
            return role.value
        else:
            return "innocent"

    def _construct_confidentially_revealing_game_state_sync_event(
        self, viewer_role: Role
    ):
        winner = self.game_state.winner
        if winner is not None:
            winner = winner.value
        # Warning - this will reveal all roles!
        return GameStateSync(
            type="game.state",
            payload=GameStateSyncPayload(
                players=[
                    PlayerState(
                        player_id=k,
                        name=self.player_names[k],
                        alive=v["alive"],
                        role_revealed=self._confidentially_reveal_role(
                            v["role"], viewer_role
                        ),
                    )
                    for k, v in self.game_state.players.items()
                ],
                phase=self.game_state.phase.value,
                votes=self.cast_votes,
                winner=winner,
                logs=self.event_log,
            ),
        )

    def _construct_revealing_game_state_sync_event(self):
        winner = self.game_state.winner
        if winner is not None:
            winner = winner.value
        # Warning - this will reveal all roles!
        return GameStateSync(
            type="game.state",
            payload=GameStateSyncPayload(
                players=[
                    PlayerState(
                        player_id=k,
                        name=self.player_names[k],
                        alive=v["alive"],
                        role_revealed=v["role"].value,
                    )
                    for k, v in self.game_state.players.items()
                ],
                phase=self.game_state.phase.value,
                votes=self.cast_votes,
                winner=winner,
                logs=self.event_log,
            ),
        )

    def _sync_game_state(self):
        for uuid, pa in self.players.items():
            pa.receive_event(
                self._construct_confidentially_revealing_game_state_sync_event(
                    self.game_state.players[uuid]["role"]
                )
            )

    def _check_game_over(self):
        game_over = self.game_state.check_game_over()
        if game_over:
            self._broadcast(self._construct_revealing_game_state_sync_event())

    def _end_night(self):
        vote_winner = self._get_vote_winner()
        self.game_state.end_night(vote_winner)

        if vote_winner:
            self._broadcast(
                MorningNews(
                    type="action.morning_news",
                    payload=MorningNewsPayload(target_id=vote_winner),
                )
            )
        self._reset_votes()

        self.next_phase_timestamp = datetime.now(tz=timezone.utc) + timedelta(
            seconds=self.day_duration_s
        )
        self._broadcast(
            PhaseChange(
                type="phase.change",
                payload=PhaseChangePayload(
                    phase="day", ends_at=self.next_phase_timestamp
                ),
            )
        )
        self._sync_game_state()
        self._check_game_over()

    def _end_day(self):
        self.game_state.end_day()
        self._reset_votes()
        self.next_phase_timestamp = datetime.now(tz=timezone.utc) + timedelta(
            seconds=self.vote_duration_s
        )
        self._broadcast(
            PhaseChange(
                type="phase.change",
                payload=PhaseChangePayload(
                    phase="voting", ends_at=self.next_phase_timestamp
                ),
            )
        )
        self._sync_game_state()

    def _end_voting(self):
        vote_winner = self._get_vote_winner()
        self.game_state.end_voting(vote_winner)

        if vote_winner:
            self._broadcast(
                EveningNews(
                    type="action.evening_news",
                    payload=EveningNewsPayload(target_id=vote_winner),
                )
            )
        self._reset_votes()

        self.next_phase_timestamp = datetime.now(tz=timezone.utc) + timedelta(
            seconds=self.night_duration_s
        )
        self._broadcast(
            PhaseChange(
                type="phase.change",
                payload=PhaseChangePayload(
                    phase="night", ends_at=self.next_phase_timestamp
                ),
            )
        )
        self._sync_game_state()
        self._check_game_over()

    def _tick(self):
        # reset the timer to one minute, ad infinitum
        if self.lobby and len(self.players) < 4:
            self.next_phase_timestamp = datetime.now(tz=timezone.utc) + timedelta(
                minutes=1, milliseconds=499
            )
        elif self.next_phase_timestamp <= datetime.now(tz=timezone.utc):
            if self.lobby:
                self.lobby = False
                # TODO: randomly choose roles here
            elif self.game_state.phase == Phase.NIGHT:
                self._end_night()
            elif self.game_state.phase == Phase.DAY:
                self._end_day()
            elif self.game_state.phase == Phase.VOTING:
                self._end_voting()

    def receive_event(self, event: GameEvent, player: PlayerAdapter):
        match event:
            case PlayerJoin(payload=payload):
                self.add_player(payload.player_id, payload.name, player)
                self._broadcast(
                    PlayerJoined(
                        type="player.joined",
                        payload=PlayerJoinedPayload(
                            player_id=payload.player_id, name=payload.player_id
                        ),
                    )
                )
            case PlayerLeave(payload=payload):
                self.remove_player(payload.player_id)
                self._broadcast(
                    PlayerLeft(
                        type="player.left",
                        payload=PlayerLeftPayload(player_id=payload.player_id),
                    )
                )
            case NightAction(payload=payload):
                if (
                    self.game_state.phase == Phase.NIGHT
                    and self.game_state.players[payload.actor_id]["role"] == Role.MAFIA
                ):
                    # TODO: change vote count actually
                    self._broadcast(
                        VoteCast(
                            type="action.vote_cast",
                            payload=VoteCastPayload(
                                actor_id=payload.actor_id, target_id=payload.target_id
                            ),
                        ),
                        included_player_roles=[Role.MAFIA],
                    )
                    player.receive_event(
                        ActionAck(
                            type="action.ack",
                            payload=ActionAckPayload(
                                success=True, message="Successfully cast vote"
                            ),
                        )
                    )
                else:
                    player.receive_event(
                        ActionAck(
                            type="action.ack",
                            payload=ActionAckPayload(
                                success=False, message="Cannot do this!"
                            ),
                        )
                    )
            case Vote(payload=payload):
                if self.game_state.phase == Phase.VOTING:
                    # TODO: change vote count actually
                    self._broadcast(
                        VoteCast(
                            type="action.vote_cast",
                            payload=VoteCastPayload(
                                actor_id=payload.actor_id, target_id=payload.target_id
                            ),
                        )
                    )
                    player.receive_event(
                        ActionAck(
                            type="action.ack",
                            payload=ActionAckPayload(
                                success=True, message="Successfully cast vote"
                            ),
                        )
                    )
                else:
                    player.receive_event(
                        ActionAck(
                            type="action.ack",
                            payload=ActionAckPayload(
                                success=False, message="Cannot do this!"
                            ),
                        )
                    )
            case SendMessage(payload=payload):
                if self.lobby or self.game_state.phase == Phase.DAY:
                    self._broadcast(
                        MessageReceived(type="message.received", payload=payload)
                    )
                else:
                    player.receive_event(
                        ActionAck(
                            type="action.ack",
                            payload=ActionAckPayload(
                                success=False, message="Cannot do this!"
                            ),
                        )
                    )

        self._tick()
