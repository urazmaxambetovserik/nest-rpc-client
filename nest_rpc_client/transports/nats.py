import json
import uuid

import nats
from nats.aio.client import Client

from ..config.nats import NATSConfig
from ..transport import Transport


class NATSTransport(Transport):
    config: NATSConfig
    client: Client

    def __init__(self, config: NATSConfig):
        self.config = config

    async def connect(self) -> None:
        self.client = await nats.connect(self.config.servers)

    async def close(self) -> None:
        if not hasattr(self, "client"):
            return
        if not self.client.is_connected:
            return

        await self.client.close()

    async def send(self, pattern: str, data: dict) -> dict:
        correlation_id = str(uuid.uuid4())
        message = json.dumps(
            {"id": correlation_id, "pattern": pattern, "data": data}
        ).encode("utf-8")

        msg = await self.client.request(
            pattern, message, timeout=self.config.response_timeout
        )
        response_data: dict = json.loads(msg.data)

        if response_data.get("id") != correlation_id:
            raise ValueError("Correlation ID mismatch")

        return response_data["response"]

    async def emit(self, pattern: str, data: dict) -> None:
        await self.client.publish(
            pattern,
            json.dumps(
                {"pattern": pattern, "data": data},
            ).encode("utf-8"),
        )
