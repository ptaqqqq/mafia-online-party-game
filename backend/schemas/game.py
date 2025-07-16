from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import Field

# to use camelCase when serializing/deserializing JSON
from fastapi_camelcase import CamelModel


# Player events


class PlayerJoinPayload(CamelModel):
    player_id: str = Field(..., description="UUID of the joining player")
    name: str = Field(..., description="Display name")


class PlayerJoin(CamelModel):
    type: Literal["player.join"]
    payload: PlayerJoinPayload


class PlayerLeavePayload(CamelModel):
    player_id: str = Field(..., description="UUID of the leaving player")


class PlayerLeave(CamelModel):
    type: Literal["player.leave"]
    payload: PlayerLeavePayload


class PlayerJoinedPayload(CamelModel):
    player_id: str = Field(..., description="UUID of the player who joined")
    name: str = Field(..., description="Display name")


class PlayerJoined(CamelModel):
    type: Literal["player.joined"]
    payload: PlayerJoinedPayload


class PlayerLeftPayload(CamelModel):
    player_id: str = Field(..., description="UUID of the player who left")


class PlayerLeft(CamelModel):
    type: Literal["player.left"]
    payload: PlayerLeftPayload


# Game events


class NightActionPayload(CamelModel):
    actor_id: str = Field(..., description="UUID of the player performing the action")
    action: Literal["kill"]
    target_id: str = Field(..., description="UUID of the targeted player")


class NightAction(CamelModel):
    type: Literal["action.night"]
    payload: NightActionPayload


class VotePayload(CamelModel):
    actor_id: str = Field(..., description="UUID of the player voting")
    target_id: str = Field(..., description="UUID of the player voted on")


class Vote(CamelModel):
    type: Literal["action.vote"]
    payload: VotePayload


class ActionAckPayload(CamelModel):
    success: bool
    message: Optional[str] = None


class ActionAck(CamelModel):
    type: Literal["action.ack"]
    payload: ActionAckPayload


class MorningNewsPayload(CamelModel):
    target_id: str = Field(..., description="UUID of the killed player")


class MorningNews(CamelModel):
    type: Literal["action.news"]
    payload: MorningNewsPayload


class VoteCastPayload(CamelModel):
    actor_id: str = Field(..., description="UUID of the player voting")
    target_id: str = Field(..., description="UUID of the player voted on")


class VoteCast(CamelModel):
    type: Literal["action.vote_cast"]
    payload: VoteCastPayload


# Phase change events


class PhaseChangePayload(CamelModel):
    phase: Literal["day", "night", "voting"]
    ends_at: datetime = Field(..., description="When this phase ends (ISO timestamp)")


class PhaseChange(CamelModel):
    type: Literal["phase.change"]
    payload: PhaseChangePayload


# Chat message events


class MessagePayload(CamelModel):
    actor_id: str = Field(..., description="UUID of the player sending the message")
    timestamp: datetime = Field(
        ..., description="When this message was sent (ISO timestamp)"
    )
    text: str = Field(..., description="Text content of the message")


class SendMessage(CamelModel):
    type: Literal["message.send"]
    payload: MessagePayload


class MessageReceived(CamelModel):
    type: Literal["message.received"]
    payload: MessagePayload


# Game state sync


class PlayerState(CamelModel):
    player_id: str
    name: str
    alive: bool
    role_revealed: Optional[str] = None


class GameLogEntry(CamelModel):
    timestamp: datetime = Field(
        ..., description="When this event occured (ISO timestamp)"
    )
    event: str = Field(..., description="Type of the event (player.joined, action.ack)")
    details: Dict[str, Any] = Field(..., description="Payload of the event")


class GameStatePayload(CamelModel):
    players: List[PlayerState]
    phase: Literal["day", "night", "voting", "ended"] = Field(
        ..., description="Current game phase"
    )
    votes: Optional[Dict[str, str]] = Field(
        None, description="Maps actor: target during voting phase"
    )
    winner: Optional[Literal["mafia", "innocents", "draw"]] = Field(
        None, description="Who won the game (if it ended)"
    )
    logs: List[GameLogEntry] = Field(
        ..., description="Past game events, chronologically"
    )


class GameState(CamelModel):
    type: Literal["game.state"]
    payload: GameStatePayload
