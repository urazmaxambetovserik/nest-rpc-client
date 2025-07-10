from .transport import Transport


class Client:
    def __init__(self, transport: Transport):
        self.transport = transport

    async def connect(self) -> None:
        await self.transport.connect()

    async def close(self) -> None:
        await self.transport.close()

    async def send(self, pattern: str, data: dict) -> dict:
        return await self.transport.send(pattern, data)

    async def emit(self, pattern: str, data: dict) -> None:
        return await self.transport.emit(pattern, data)

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
