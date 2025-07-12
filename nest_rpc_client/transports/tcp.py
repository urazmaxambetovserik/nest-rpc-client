import asyncio
import json
import uuid

from ..config.tcp import TCPConfig
from ..transport import Transport


class TCPTransport(Transport):
    config: TCPConfig
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter

    def __init__(self, config: TCPConfig):
        self.config = config
        self.reader = None  # type: ignore
        self.writer = None  # type: ignore

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(
            self.config.host,
            self.config.port,
        )

    async def close(self):
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()

    async def send(self, pattern: str, data: dict) -> dict:
        correlation_id = str(uuid.uuid4())
        body = json.dumps(
            {"id": correlation_id, "pattern": pattern, "data": data},
        )
        body_with_length = f"{len(body)}#{body}"

        self.writer.write(body_with_length.encode("utf-8"))
        await self.writer.drain()

        buffer = ""
        while True:
            chunk = (await self.reader.read(4096)).decode()
            if not chunk:
                break

            buffer += chunk
            if "#" in buffer:
                break

        length_str, rest = buffer.split("#", 1)
        expected_length = int(length_str)

        while len(rest) < expected_length:
            rest += (await self.reader.read(4096)).decode()

        response_json = json.loads(rest[:expected_length])
        return response_json["response"]

    async def emit(self, pattern: str, data: dict) -> None:
        payload = {"pattern": pattern, "data": data}
        body = json.dumps(payload)
        body_with_length = f"{len(body)}#{body}"

        self.writer.write(body_with_length.encode("utf-8"))
        await self.writer.drain()
