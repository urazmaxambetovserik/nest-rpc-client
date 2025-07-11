from ..config.redis import RedisConfig
from ..transport import Transport


class RedisTransport(Transport):
    config: RedisConfig

    def __init__(self, config: RedisConfig):
        self.config = config

    async def connect(self) -> None:
        raise NotImplementedError()

    async def close(self) -> None:
        raise NotImplementedError()

    async def send(self, pattern: str, data: dict) -> dict:
        raise NotImplementedError()

    async def emit(self, pattern: str, data: dict) -> None:
        raise NotImplementedError()
