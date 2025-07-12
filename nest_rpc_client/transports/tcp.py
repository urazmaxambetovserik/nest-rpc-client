import asyncio

from ..config.tcp import TCPConfig
from ..transport import Transport


class TCPTransport(Transport):
    config: TCPConfig
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter

    def __init__(self, config: TCPConfig):
        self.config = config

    async def connect(self):
        raise NotImplementedError

    async def close(self):
        raise NotImplementedError

    async def send(self, pattern: str, data: dict) -> dict:
        raise NotImplementedError

    async def emit(self, pattern: str, data: dict) -> None:
        raise NotImplementedError
