from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from schemas.game import GameEvent, GameLogEntry, GameStateSync, GameStateSyncPayload, MorningNews, MorningNewsPayload, PlayerState
from app.domain.game_state import GameState, Phase


class PlayerAdapter(ABC):
    @abstractmethod
    def receive_event(self, event: GameEvent):
        raise NotImplementedError


class GameManager:
    def __init__(self, night_duration_s=30, day_durations_s=60, vote_duration_s=30):
        self.game_state = GameState()
        self.players: Dict[str, PlayerAdapter] = defaultdict()
        self.player_names: Dict[str, str] = defaultdict()
        self.lobby = True
        self.next_phase_timestamp: datetime = datetime.now() + timedelta(
            minutes=1, milliseconds=499
        )
        self.night_duration_s = night_duration_s
        self.day_duration_s = day_durations_s
        self.vote_duration_s = vote_duration_s
        self.cast_votes: Dict[str, int] = defaultdict()
        self.event_log: List[GameLogEntry] = []

    def _broadcast(self, event: GameEvent, excluded_player_ids=[]):
        for uuid, player in self.players.items():
            if uuid not in excluded_player_ids:
                player.receive_event(event)

    def add_player(self, uuid: str, player: PlayerAdapter):
        self.players[uuid] = player
        self.player_names[uuid] = uuid

    def remove_player(self, uuid: str):
        del self.players[uuid]
        del self.player_names[uuid]

    def _reset_votes(self):
        self.cast_votes = defaultdict()
        for uuid in self.players.keys():
            self.cast_votes[uuid] = 0

    def _get_vote_winner(self):
        max_count = max(self.cast_votes.values())
        winners = [k for k, v in self.cast_votes.items() if v == max_count]
        if len(winners) == 1:
            return winners[0]
        else:
            return None

    def _construct_revealing_game_state_sync_event(self):
        winner = self.game_state.winner
        if winner is not None:
            winner = winner.value
        # Warning - this will reveal all roles!
        return GameStateSync(
            type="game.state",
            payload=GameStateSyncPayload(
                players=[PlayerState(
                        player_id=k, 
                        name=self.player_names[k], 
                        alive=v["alive"], 
                        role_revealed=v["role"].value) 
                    for k, v in self.game_state.players.items()
                ],
                phase=self.game_state.phase.value,
                votes=self.cast_votes,
                winner=winner,
                logs=self.event_log
            )
        )

    def _end_night(self):
        vote_winner = self._get_vote_winner()
        self.game_state.end_night(vote_winner)

        if vote_winner:
            self._broadcast(MorningNews(type="action.news", payload=MorningNewsPayload(target_id=vote_winner)))

        game_over = self.game_state.check_game_over()
        if game_over:
            self._broadcast(self._construct_revealing_game_state_sync_event())

    def tick(self):
        # reset the timer to one minute, ad infinitum
        if self.lobby and len(self.players) < 4:
            self.next_phase_timestamp = datetime.now() + timedelta(
                minutes=1, milliseconds=499
            )
        elif self.next_phase_timestamp <= datetime.now():
            if self.lobby:
                self.lobby = False
            elif self.game_state.phase == Phase.NIGHT:
                self._end_night()
            else:
                # TODO:
                raise NotImplementedError


    def receive_event(self, event: GameEvent):
        raise NotImplementedError
