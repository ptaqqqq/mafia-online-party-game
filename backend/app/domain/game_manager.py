from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime, timedelta, timezone
import random
from typing import Dict, List
from schemas.game import (
    ActionAck,
    ActionAckPayload,
    EveningNews,
    EveningNewsPayload,
    GameEvent,
    GameLogEntry,
    GameStateRequest,
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
    async def receive_event(self, event: GameEvent):
        raise NotImplementedError


# TODO: refactor to return events, not send them - race conditions!
class GameManager:
    def __init__(
        self,
        mafiosi_count: int = 2,
        night_duration_s=20,
        day_duration_s=15,
        vote_duration_s=20,
        lobby_duration_s=30,
        ended_duation_s=30
    ):
        self.mafiosi_count = mafiosi_count
        self.night_duration_s = night_duration_s
        self.day_duration_s = day_duration_s
        self.vote_duration_s = vote_duration_s
        self.lobby_duration_s = lobby_duration_s
        self.ended_duration_s = ended_duation_s

        self.game_state = GameState()
        self.players: Dict[str, PlayerAdapter] = dict()
        self.player_names: Dict[str, str] = dict()
        self.lobby = True
        self.next_phase_timestamp: float = (datetime.now(tz=timezone.utc) + timedelta(
            minutes=1, milliseconds=499
        )).timestamp()
        self.cast_votes: Dict[str, str] = defaultdict(str)
        self.event_log: List[GameLogEntry] = []

    async def _broadcast(
        self, event: GameEvent, excluded_player_ids=None, included_player_roles=None
    ):
        excluded_player_ids = excluded_player_ids or []
        included_player_roles = included_player_roles or []
        for uuid, player in self.players.items():
            if uuid not in excluded_player_ids and (
                len(included_player_roles) == 0
                or self.game_state.players[uuid]["role"] in included_player_roles
            ):
                await player.receive_event(event)

    def _add_default_state_player_to_game_state(self, uuid: str):
        self.game_state.add_player(
            uuid, PlayerGameState(role=Role.INNOCENT, alive=True)
        )

    def add_player(self, uuid: str, name: str, player: PlayerAdapter):
        self.players[uuid] = player
        self.player_names[uuid] = name
        self._add_default_state_player_to_game_state(uuid)

    def remove_player(self, uuid: str):
        del self.players[uuid]
        del self.player_names[uuid]
        self.game_state.remove_player(uuid)

    def _reset_votes(self):
        self.cast_votes = defaultdict(str)

    def _get_vote_winner(self):
        if len(self.cast_votes) == 0:
            return None
        vote_count = defaultdict(int)
        for _, target in self.cast_votes.items():
            vote_count[target] += 1
        max_count = max(vote_count.values())
        winners = [k for k, v in vote_count.items() if v == max_count]
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
                phase=("lobby" if self.lobby else self.game_state.phase.value),
                phase_ends_at=self.next_phase_timestamp,
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
                phase=("lobby" if self.lobby else self.game_state.phase.value),
                phase_ends_at=self.next_phase_timestamp,
                votes=self.cast_votes,
                winner=winner,
                logs=self.event_log,
            ),
        )

    async def _sync_game_state(self):
        for uuid, pa in self.players.items():
            await pa.receive_event(
                self._construct_confidentially_revealing_game_state_sync_event(
                    self.game_state.players[uuid]["role"]
                )
            )

    async def _end_game(self):
        self.next_phase_timestamp = (datetime.now(tz=timezone.utc) + timedelta(seconds=self.ended_duration_s)).timestamp()
        await self._broadcast(self._construct_revealing_game_state_sync_event())
        await self._broadcast(PhaseChange(type="phase.change", payload=PhaseChangePayload(phase="ended", ends_at=self.next_phase_timestamp)))

    async def _check_game_over(self):
        game_over = self.game_state.check_game_over()
        if game_over:
            await self._end_game()


    async def _end_night(self):
        vote_winner = self._get_vote_winner()
        self.game_state.end_night(vote_winner)

        if vote_winner:
            await self._broadcast(
                MorningNews(
                    type="action.morning_news",
                    payload=MorningNewsPayload(target_id=vote_winner),
                )
            )
        self._reset_votes()

        self.next_phase_timestamp = (datetime.now(tz=timezone.utc) + timedelta(
            seconds=self.day_duration_s
        )).timestamp()
        await self._broadcast(
            PhaseChange(
                type="phase.change",
                payload=PhaseChangePayload(
                    phase="day", ends_at=self.next_phase_timestamp
                ),
            )
        )
        await self._sync_game_state()
        await self._check_game_over()

    async def _end_day(self):
        self.game_state.end_day()
        self._reset_votes()
        self.next_phase_timestamp = (datetime.now(tz=timezone.utc) + timedelta(
            seconds=self.vote_duration_s
        )).timestamp()
        await self._broadcast(
            PhaseChange(
                type="phase.change",
                payload=PhaseChangePayload(
                    phase="voting", ends_at=self.next_phase_timestamp
                ),
            )
        )
        await self._sync_game_state()

    async def _end_voting(self):
        vote_winner = self._get_vote_winner()
        self.game_state.end_voting(vote_winner)

        if vote_winner:
            await self._broadcast(
                EveningNews(
                    type="action.evening_news",
                    payload=EveningNewsPayload(target_id=vote_winner),
                )
            )
        self._reset_votes()

        self.next_phase_timestamp = (datetime.now(tz=timezone.utc) + timedelta(
            seconds=self.night_duration_s
        )).timestamp()
        await self._broadcast(
            PhaseChange(
                type="phase.change",
                payload=PhaseChangePayload(
                    phase="night", ends_at=self.next_phase_timestamp
                ),
            )
        )
        await self._sync_game_state()
        await self._check_game_over()

    async def _restart_game(self):
        self._reset_votes()
        self.lobby = True
        self.next_phase_timestamp = (datetime.now(tz=timezone.utc) + timedelta(seconds=self.lobby_duration_s)).timestamp()
        self.game_state = GameState()
        for player_uuid in self.players.keys():
            self._add_default_state_player_to_game_state(player_uuid)
        await self._sync_game_state()
        await self._broadcast(PhaseChange(type="phase.change", payload=PhaseChangePayload(phase="lobby", ends_at=self.next_phase_timestamp)))

    def _assign_roles_randomly(self):
        uuid_list = list(self.players.keys())
        if len(uuid_list) <= 4:
            # Otherwise the game ends instantly
            self.mafiosi_count = 1
        mafia_uuids = random.sample(uuid_list, k=self.mafiosi_count)
        for uuid in uuid_list:
            if uuid in mafia_uuids:
                self.game_state.players[uuid]["role"] = Role.MAFIA
            else:
                self.game_state.players[uuid]["role"] = Role.INNOCENT

    async def _tick(self):
        # reset the timer to one minute, ad infinitum
        if self.lobby and len(self.players) < 4:
            self.next_phase_timestamp = (datetime.now(tz=timezone.utc) + timedelta(
                seconds=self.lobby_duration_s
            )).timestamp()
        elif self.next_phase_timestamp <= datetime.now(tz=timezone.utc).timestamp():
            if self.lobby:
                self.lobby = False
                self.next_phase_timestamp = (datetime.now(tz=timezone.utc) + timedelta(seconds=self.night_duration_s)).timestamp()
                self._assign_roles_randomly()
                self._reset_votes()
            elif self.game_state.phase == Phase.NIGHT:
                await self._end_night()
            elif self.game_state.phase == Phase.DAY:
                await self._end_day()
            elif self.game_state.phase == Phase.VOTING:
                await self._end_voting()
            elif self.game_state.phase == Phase.ENDED:
                await self._restart_game()
        await self._sync_game_state()

    async def _receive_vote(self, voter: PlayerAdapter, vote: Vote | NightAction):
        payload = vote.payload
        self.cast_votes[payload.actor_id] = payload.target_id
        await self._broadcast(
            VoteCast(
                type="action.vote_cast",
                payload=VoteCastPayload(
                    actor_id=payload.actor_id, target_id=payload.target_id
                ),
            ),
            included_player_roles=[Role.MAFIA],
        )
        await voter.receive_event(
            ActionAck(
                type="action.ack",
                payload=ActionAckPayload(
                    success=True, message="Successfully cast vote"
                ),
            )
        )

    async def receive_event(self, event: GameEvent, player: PlayerAdapter):
        match event:
            case PlayerJoin(type="player.join", payload=payload):
                self.add_player(payload.player_id, payload.name, player)
                await self._broadcast(
                    PlayerJoined(
                        type="player.joined",
                        payload=PlayerJoinedPayload(
                            player_id=payload.player_id, name=payload.player_id
                        ),
                    )
                )
                await self._sync_game_state()
            case PlayerLeave(payload=payload):
                if payload.player_id in self.players:
                    self.remove_player(payload.player_id)
                    await self._broadcast(
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
                    await self._receive_vote(player, event)
                else:
                    await player.receive_event(
                        ActionAck(
                            type="action.ack",
                            payload=ActionAckPayload(
                                success=False, message="Cannot do this!"
                            ),
                        )
                    )
            case Vote(payload=payload):
                if self.game_state.phase == Phase.VOTING:
                    await self._receive_vote(player, event)
                else:
                    await player.receive_event(
                        ActionAck(
                            type="action.ack",
                            payload=ActionAckPayload(
                                success=False, message="Cannot do this!"
                            ),
                        )
                    )
            case SendMessage(payload=payload):
                if self.lobby or self.game_state.phase == Phase.DAY:
                    await self._broadcast(
                        MessageReceived(type="message.received", payload=payload)
                    )
                else:
                    await player.receive_event(
                        ActionAck(
                            type="action.ack",
                            payload=ActionAckPayload(
                                success=False, message="Cannot do this!"
                            ),
                        )
                    )
            case GameStateRequest(type="game.sync_request", player_id=player_id):
                await player.receive_event(
                    self._construct_confidentially_revealing_game_state_sync_event(self.game_state.players[player_id]["role"]),
                )
            case _:
                await player.receive_event(
                    ActionAck(
                        type="action.ack",
                        payload=ActionAckPayload(
                            success=False, message="Cannot do this!"
                        ),
                    )
                )

        await self._tick()
