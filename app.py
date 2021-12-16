"""Тестовое задание на Frontend разработчика."""
import os
import time
import random
import logging
from typing import List
from datetime import datetime
import uuid

from enum import Enum

from pydantic import BaseModel, Field

from fastapi import FastAPI, WebSocket
from fastapi.responses import RedirectResponse

from fastapi.exceptions import HTTPException
from fastapi.websockets import WebSocketDisconnect

app = FastAPI(
    title="Тестовое задание на Frontend разработчика"
)

LOGGER = logging.getLogger(__name__)

MIN_DEVICES = int(os.environ.get('MIN_DEVICES', 3))
MAX_DEVICES = int(os.environ.get('MAX_DEVICES', 7))
DEVICE_COUNT = random.randint(MIN_DEVICES, MAX_DEVICES)

FASTAPI_PORT = int(os.environ.get('FASTAPI_PORT', 8000))


class Device(BaseModel):
    """Устройство."""

    id: int
    name: str


class EventType(str, Enum):
    """Типы событий телеметрии."""

    info = "INFO"
    warn = "WARNING"
    error = "ERROR"

class Message():
    nouns = ("puppy", "car", "rabbit", "girl", "monkey")
    verbs = ("runs", "hits", "jumps", "drives", "barfs")
    adv = ("crazily.", "dutifully.", "foolishly.", "merrily.", "occasionally.")
    adj = ("adorable", "clueless", "dirty", "odd", "stupid")

    @classmethod
    def generate(self):
        l = [self.nouns,self.verbs,self.adj,self.adv]
        return ' '.join([random.choice(i) for i in l])


class TelemetryMessage(BaseModel):
    """Сообщение телеметрии."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    device_id: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    event_type: EventType = Field(
        default_factory=lambda: random.choice(
            ["INFO", "WARNING", "ERROR"]
        )
    )
    message: str = Field(
        default_factory=lambda: Message.generate()
    )


@app.get(
    "/",
    summary="Редирект на /docs"
)
async def get():
    """Редирект на /docs."""
    return RedirectResponse("http://localhost:8000/docs")


@app.get(
    "/devices",
    summary="Получить список устройств",
    response_model=List[Device]
)
async def get_devices() -> List[Device]:
    """Получить список устройств."""
    global DEVICE_COUNT
    DEVICE_COUNT = random.randint(MIN_DEVICES, MAX_DEVICES)
    return [
        Device(
            id=i,
            name=f"Device {i}",
        )
        for i in range(1, DEVICE_COUNT+1)
    ]


@app.get(
    "/test/telemetry/{device_id}",
    summary="Получить тестовое сообщение с устройства",
    response_model=TelemetryMessage
)
async def get_telemetry(device_id: int) -> TelemetryMessage:
    """Получить тестовое сообщение с устройства."""
    if device_id >= DEVICE_COUNT:

        message = (
            f"No such device id {device_id}, "
            f"Available devices: 0-{DEVICE_COUNT - 1}"
        )
        LOGGER.error(message)
        raise HTTPException(
            status_code=404,
            detail=message
        )

    return TelemetryMessage(device_id=device_id)


@app.websocket("/ws/telemetry/{device_id}")
async def websocket_telemetry(websocket: WebSocket, device_id: int):
    """Вебсокет телеметрии."""
    await websocket.accept()

    message = "Client connected to device {device_id}"
    LOGGER.info(message)
    try:
        if device_id >= DEVICE_COUNT:

            message = (
                f"No such device id {device_id}, "
                f"Available devices: 0-{DEVICE_COUNT - 1}"
            )
            LOGGER.error(message)
            await websocket.close(code=404)
            return

        while True:
            await websocket.send_text(
                data=TelemetryMessage(device_id=device_id).json()
            )
            time.sleep(random.random() * 3)
    except WebSocketDisconnect:
        message = "Client desconnected from device {device_id}"
        LOGGER.info(message)
