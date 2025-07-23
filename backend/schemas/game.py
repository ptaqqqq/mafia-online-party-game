from typing import Any, Dict, List, Literal, Optional
from pydantic import Field

from fastapi_camelcase import CamelModel


class GameEvent(CamelModel):
    pass

class PlayerJoinPayload(CamelModel):
    player_id: str = Field(..., description="UUID of the joining player")
    name: str = Field(..., description="Display name")


class PlayerJoin(GameEvent):
    type: Literal["player.join"]
    payload: PlayerJoinPayload


class PlayerLeavePayload(CamelModel):
    player_id: str = Field(..., description="UUID of the leaving player")


class PlayerLeave(GameEvent):
    type: Literal["player.leave"]
    payload: PlayerLeavePayload


class PlayerJoinedPayload(CamelModel):
    player_id: str = Field(..., description="UUID of the player who joined")
    name: str = Field(..., description="Display name")


class PlayerJoined(GameEvent):
    type: Literal["player.joined"]
    payload: PlayerJoinedPayload


class PlayerLeftPayload(CamelModel):
    player_id: str = Field(..., description="UUID of the player who left")


class PlayerLeft(GameEvent):
    type: Literal["player.left"]
    payload: PlayerLeftPayload


class NightActionPayload(CamelModel):
    actor_id: str = Field(..., description="UUID of the player performing the action")
    action: Literal["kill", "heal"]
    target_id: str = Field(..., description="UUID of the targeted player")


class NightAction(GameEvent):
    type: Literal["action.night"]
    payload: NightActionPayload


class VotePayload(CamelModel):
    actor_id: str = Field(..., description="UUID of the player voting")
    target_id: str = Field(..., description="UUID of the player voted on")


class Vote(GameEvent):
    type: Literal["action.vote"]
    payload: VotePayload


class ActionAckPayload(CamelModel):
    success: bool
    message: Optional[str] = None


class ActionAck(GameEvent):
    type: Literal["action.ack"]
    payload: ActionAckPayload


class MorningNewsPayload(CamelModel):
    target_id: str = Field(..., description="UUID of the killed player")


class MorningNews(GameEvent):
    type: Literal["action.morning_news"]
    payload: MorningNewsPayload


class EveningNewsPayload(CamelModel):
    target_id: str = Field(..., description="UUID of the ostracized player")


class EveningNews(GameEvent):
    type: Literal["action.evening_news"]
    payload: EveningNewsPayload



class VoteCastPayload(CamelModel):
    actor_id: str = Field(..., description="UUID of the player voting")
    target_id: str = Field(..., description="UUID of the player voted on")


class VoteCast(GameEvent):
    type: Literal["action.vote_cast"]
    payload: VoteCastPayload


class PhaseChangePayload(CamelModel):
    phase: Literal["lobby", "character_intro", "day", "night", "voting", "ended"]
    ends_at: float = Field(..., description="When this phase ends (Unix timestamp)")


class PhaseChange(GameEvent):
    type: Literal["phase.change"]
    payload: PhaseChangePayload


class MessagePayload(CamelModel):
    actor_id: str = Field(..., description="UUID of the player sending the message")
    timestamp: float = Field(
        ..., description="When this message was sent (Unix timestamp)"
    )
    text: str = Field(..., description="Text content of the message")


class SendMessage(GameEvent):
    type: Literal["message.send"]
    payload: MessagePayload


class MessageReceived(GameEvent):
    type: Literal["message.received"]
    payload: MessagePayload


class NarratorMessagePayload(CamelModel):
    text: str = Field(..., description="Narrator message text")
    timestamp: float = Field(
        ..., description="When this message was sent (Unix timestamp)"
    )


class NarratorMessage(GameEvent):
    type: Literal["narrator.message"]
    payload: NarratorMessagePayload


class OpeningStoryRequest(GameEvent):
    type: Literal["opening.story_request"]


class PlayerState(CamelModel):
    player_id: str
    name: str
    alive: bool
    role_revealed: Optional[str] = None


class GameLogEntry(CamelModel):
    timestamp: float = Field(
        ..., description="When this event occured (Unix timestamp)"
    )
    event: str = Field(..., description="Type of the event (player.joined, action.ack)")
    details: Dict[str, Any] = Field(..., description="Payload of the event")


class GameStateSyncPayload(CamelModel):
    players: List[PlayerState]
    phase: Literal["lobby", "character_intro", "day", "night", "voting", "ended"] = Field(
        ..., description="Current game phase"
    )
    phase_ends_at: float = Field(..., description="When this phase ends (Unix timestamp)")
    votes: Optional[Dict[str, str]] = Field(
        None, description="Maps voter: target during voting phase"
    )
    winner: Optional[Literal["mafia", "innocents", "draw"]] = Field(
        None, description="Who won the game (if it ended)"
    )
    logs: List[GameLogEntry] = Field(
        ..., description="Past game events, chronologically"
    )


class GameStateSync(GameEvent):
    type: Literal["game.state"]
    payload: GameStateSyncPayload


class GameStateRequest(GameEvent):
    type: Literal["game.sync_request"]
    player_id: str


class CharacterProfilePayload(CamelModel):
    player_id: str = Field(..., description="UUID of the player")
    name: str = Field(..., description="Display name of the player")
    profession: str = Field(..., description="Character profession")
    description: str = Field(..., description="Character description generated by LLM")
    emoji: str = Field(..., description="Emoji representing the profession")
    current_index: int = Field(..., description="Current profile being shown (1-based)")
    total_count: int = Field(..., description="Total number of profiles to show")


class CharacterProfile(GameEvent):
    type: Literal["character.profile"]
    payload: CharacterProfilePayload


class ProfilesStartPayload(CamelModel):
    total_count: int = Field(..., description="Total number of profiles that will be shown")


class ProfilesStart(GameEvent):
    type: Literal["character.profiles_start"]
    payload: ProfilesStartPayload


class ProfilesCompletePayload(CamelModel):
    pass

class ProfilesComplete(GameEvent):
    type: Literal["character.profiles_complete"]
    payload: ProfilesCompletePayload