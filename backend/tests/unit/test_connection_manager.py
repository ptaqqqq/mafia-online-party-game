from fastapi import WebSocket
import asyncio
import pytest
from app.routers.websocket import ConnectionManager
from schemas.game import PlayerJoined, PlayerJoinedPayload


class DummyWS(WebSocket):
    def __init__(self):
        self.sent = []

    async def accept(self, *args, **kwargs):
        pass

    async def send_json(self, data, *args, **kwargs):
        self.sent.append(data)


@pytest.mark.asyncio(loop_scope="module")
async def test_connect_and_disconnect():
    mgr = ConnectionManager()
    mgr.rooms["r2"].update([])
    ws = DummyWS()

    await mgr.connect(ws, "r1")

    assert ws in mgr.rooms["r1"]
    assert ws not in mgr.rooms["r2"]

    mgr.disconnect(ws, "r1")

    assert ws not in mgr.rooms["r1"]


@pytest.mark.asyncio(loop_scope="module")
async def test_broadcast():
    mgr = ConnectionManager()
    ws1 = DummyWS()
    ws2 = DummyWS()
    ws3 = DummyWS()

    await mgr.connect(ws1, "r1")
    await mgr.connect(ws2, "r1")
    await mgr.connect(ws3, "r2")

    assert ws3 in mgr.rooms["r2"]
    assert ws3 not in mgr.rooms["r1"]

    evt = PlayerJoined(
        type="player.joined",
        payload=PlayerJoinedPayload(player_id="user-uuid", name="user123"),
    )

    await mgr.broadcast("r1", evt)

    assert ws1.sent == [evt.model_dump()]
    assert ws2.sent == [evt.model_dump()]
    assert ws3.sent == []

    mgr.disconnect(ws1, "r1")

    assert ws1 not in mgr.rooms["r1"]

    mgr.disconnect(ws2, "r1")

    assert "r1" not in mgr.rooms

    mgr.disconnect(ws3, "r2")
