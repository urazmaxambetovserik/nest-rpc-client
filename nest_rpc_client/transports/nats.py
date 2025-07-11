from ..config.nats import NATSConfig
from ..transport import Transport


class NATSTransport(Transport):
    def __init__(self, config: NATSConfig):
        self.config = config

    async def connect(self) -> None:
        raise NotImplementedError()

    async def close(self) -> None:
        raise NotImplementedError()

    async def send(self, pattern: str, data: dict) -> dict:
        raise NotImplementedError()

    async def emit(self, pattern: str, data: dict) -> None:
        raise NotImplementedError()
