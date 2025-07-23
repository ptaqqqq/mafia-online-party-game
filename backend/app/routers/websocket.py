from collections import defaultdict
import logging
from typing import Dict, override
from uuid import uuid4
from app.domain.game_manager import GameManager, PlayerAdapter
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.routing import APIRouter
from pydantic import ValidationError


from schemas.game import (
    ActionAck,
    ActionAckPayload,
    GameEvent,
    GameStateRequest,
    NightAction,
    OpeningStoryRequest,
    PlayerJoin,
    PlayerLeave,
    PlayerLeavePayload,
    SendMessage,
    Vote,
)


router = APIRouter()


class WebSocketPlayerAdapter(PlayerAdapter):
    def __init__(self, ws: WebSocket):
        self.ws = ws
        self.open = True

    @override
    async def receive_event(self, event: GameEvent):
        try:
            if self.open:
                json_data = event.model_dump_json()
                logging.info(f"Sending event {json_data}")
                await self.ws.send_text(json_data)
        except (WebSocketDisconnect, RuntimeError) as e:
            logging.warning(f"{e}")
            self.open = False


room_game_managers: Dict[str, GameManager] = defaultdict(GameManager)

# maps uuid to adapter
uuid_adapters: Dict[str, WebSocketPlayerAdapter] = {}


@router.websocket("/{room_id}")
async def websocket_endpoint(ws: WebSocket, room_id: str):
    await ws.accept()
    ws_uuid = str(uuid4())
    ws_adapter = WebSocketPlayerAdapter(ws)
    uuid_adapters[ws_uuid] = ws_adapter

    try:
        await ws.send_json({"type": "player.uuid", "payload": {"uuid": ws_uuid}})
        while True:
            try:
                msg = await ws.receive_json()

                match msg["type"]:
                    case "player.join":
                        event = PlayerJoin.model_validate(msg)
                    case "player.leave":
                        event = PlayerLeave.model_validate(msg)
                    case "action.night":
                        event = NightAction.model_validate(msg)
                    case "action.vote":
                        event = Vote.model_validate(msg)
                    case "message.send":
                        event = SendMessage.model_validate(msg)
                    case "game.sync_request":
                        event = GameStateRequest.model_validate(msg)
                    case "opening.story_request":
                        event = OpeningStoryRequest.model_validate(msg)
                    case _:
                        raise ValidationError
                await room_game_managers[room_id].receive_event(
                    event, uuid_adapters[ws_uuid]
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
    except (WebSocketDisconnect, RuntimeError):
        gm = room_game_managers[room_id]
        if ws_uuid in gm.players:
            gm.remove_player(ws_uuid)
            #await gm._broadcast(
            #    PlayerLeft(type="player.left", payload=PlayerLeftPayload(player_id=ws_uuid))
            #)
        del uuid_adapters[ws_uuid]
        if not gm.players:
            del room_game_managers[room_id]
