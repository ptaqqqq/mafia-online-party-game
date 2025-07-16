from collections import defaultdict
import json
from typing import Annotated, Dict, Set, Union
from fastapi import WebSocket, WebSocketDisconnect, WebSocketException
from fastapi.routing import APIRouter
from fastapi_camelcase import CamelModel
from pydantic import ValidationError


from shared.schemas.game import *

IncomingEvent = Annotated[
    Union[PlayerJoin, PlayerLeave, NightAction, Vote, SendMessage],
    Field(discriminator="type"),
]

OutgoingEvent = (
    PlayerJoined
    | PlayerLeft
    | ActionAck
    | MorningNews
    | VoteCast
    | PhaseChange
    | MessageReceived
    | GameState
)


class WSIncomingMessage(CamelModel):
    __root__: IncomingEvent


router = APIRouter()


class ConnectionManager:
    def __init__(self):
        # defaultdict auto creates new rooms
        self.rooms: Dict[str, Set[WebSocket]] = defaultdict(set)

    async def connect(self, ws: WebSocket, room_id: str):
        await ws.accept()
        self.rooms[room_id].add(ws)

    def disconnect(self, ws: WebSocket, room_id: str):
        self.rooms[room_id].remove(ws)
        if not self.rooms[room_id]:
            del self.rooms[room_id]

    async def broadcast(self, room_id: str, event: OutgoingEvent):
        for ws in self.rooms.get(room_id, []):
            await ws.send_json(event.model_dump())


manager = ConnectionManager()

# maps websocket to uuid
player_map: Dict[WebSocket, str] = {}


@router.websocket("/{room_id}")
async def websocket_endpoint(ws: WebSocket, room_id: str):
    await manager.connect(ws, room_id)
    try:
        while True:
            msg = await ws.receive_json()
            wrapper = WSIncomingMessage.model_validate(msg)
            event = wrapper.__root__

            # TODO: refactor
            if isinstance(event, PlayerJoin):
                pj = event
                player_map[ws] = pj.payload.player_id
                await manager.broadcast(
                    room_id,
                    PlayerJoined(
                        type="player.joined",
                        payload=PlayerJoinedPayload(
                            player_id=pj.payload.player_id, name=pj.payload.name
                        ),
                    ),
                )
            else:
                if player_map.get(ws, None) is None:
                    await ws.send_json(
                        ActionAck(
                            type="action.ack",
                            payload=ActionAckPayload(
                                success=False,
                                message="Must join before performing any actions.",
                            ),
                        ).model_dump()
                    )
                    continue

                match event:
                    case PlayerLeave(payload=PlayerLeavePayload(player_id=player_id)):
                        await manager.broadcast(
                            room_id,
                            PlayerLeft(
                                type="player.left",
                                payload=PlayerLeftPayload(player_id=player_id),
                            ),
                        )
                    case NightAction(payload=payload):
                        # TODO: gameplay logic
                        pass
                    case Vote(
                        payload=VotePayload(actor_id=actor_id, target_id=target_id)
                    ):
                        # TODO: gameplay logic + validate if possible
                        await manager.broadcast(
                            room_id,
                            VoteCast(
                                type="action.vote_cast",
                                payload=VoteCastPayload(
                                    actor_id=actor_id, target_id=target_id
                                ),
                            ),
                        )
                    case SendMessage(payload=payload):
                        # TODO: gameplay logic + validate if possible
                        await manager.broadcast(
                            room_id,
                            MessageReceived(type="message.received", payload=payload),
                        )
                    case _:
                        await ws.send_json(
                            ActionAck(
                                type="action.ack",
                                payload=ActionAckPayload(
                                    success=False,
                                    message=f"Unsupported event {msg.get("type", None)}",
                                ),
                            ).model_dump()
                        )
    except ValidationError:
        await ws.send_json(
            ActionAck(
                type="action.ack",
                payload=ActionAckPayload(
                    success=False, message="Invalid event payload"
                ),
            ).model_dump()
        )
    except WebSocketDisconnect:
        if ws in player_map:
            await manager.broadcast(
                room_id,
                PlayerLeft(
                    type="player.left",
                    payload=PlayerLeftPayload(player_id=player_map[ws]),
                ),
            )
            del player_map[ws]
        manager.disconnect(ws, room_id)
