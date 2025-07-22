from enum import Enum
from typing import Dict, Optional, TypedDict


class Phase(Enum):
    DAY = "day"
    NIGHT = "night"
    VOTING = "voting"
    ENDED = "ended"


class Role(Enum):
    INNOCENT = "innocent"
    MAFIA = "mafia"
    MEDIC = "medic"


class GameWinner(Enum):
    INNOCENT = "innocents"
    MAFIA = "mafia"
    DRAW = "draw"


class PlayerGameState(TypedDict):
    role: Role
    alive: bool


class InvalidPhaseError(Exception):
    pass


class GameState:
    def __init__(self):
        self.phase: Phase = Phase.NIGHT
        self.players: Dict[str, PlayerGameState] = {}
        self.winner: Optional[GameWinner] = None

    def add_player(self, uuid: str, player_state: PlayerGameState):
        self.players[uuid] = player_state

    def remove_player(self, uuid: str):
        del self.players[uuid]

    def end_day(self):
        if self.phase != Phase.DAY:
            raise InvalidPhaseError

        self.phase = Phase.VOTING

    def end_voting(self, suspected_player_id: Optional[str] = None):
        if self.phase != Phase.VOTING:
            raise InvalidPhaseError

        if suspected_player_id is not None:
            if self.players.get(suspected_player_id, None) is None:
                raise ValueError("Player {suspected_player} not found!")
            self.players[suspected_player_id]["alive"] = False

        if self.check_game_over():
            self.phase = Phase.ENDED
        else:
            self.phase = Phase.NIGHT

    def end_night(self, targeted_player_id: Optional[str] = None, healed_player_id: Optional[str] = None):
        if self.phase != Phase.NIGHT:
            raise InvalidPhaseError

        if targeted_player_id is not None and targeted_player_id != healed_player_id:
            if self.players.get(targeted_player_id, None) is None:
                raise ValueError(f"Player {targeted_player_id} not found!")
            self.players[targeted_player_id]["alive"] = False

        if self.check_game_over():
            self.phase = Phase.ENDED
        else:
            self.phase = Phase.DAY

    def check_game_over(self):
        mafia = sum(
            1 for p in self.players.values() if p["role"] == Role.MAFIA and p["alive"]
        )
        innocents = sum(
            1
            for p in self.players.values()
            if p["role"] in [Role.INNOCENT, Role.MEDIC] and p["alive"]
        )

        if mafia == 0:
            if innocents == 0:
                self.winner = GameWinner.DRAW
                return True
            else:
                self.winner = GameWinner.INNOCENT
                return True
        elif mafia >= innocents:
            self.winner = GameWinner.MAFIA
            return True
        else:
            self.winner = None
            return False
