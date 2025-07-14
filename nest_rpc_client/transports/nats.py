import json
import uuid

import nats
from nats.aio.client import Client

from ..config.nats import NATSConfig
from ..transport import Transport
from ..utils.parse_response import parse_response


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
        response_body: dict = json.loads(msg.data)
        return parse_response(response_body)

    async def emit(self, pattern: str, data: dict) -> None:
        await self.client.publish(
            pattern,
            json.dumps(
                {"pattern": pattern, "data": data},
            ).encode("utf-8"),
        )
