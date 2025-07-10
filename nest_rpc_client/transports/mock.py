from typing import Any

from ..transport import Transport


class MockTransport(Transport):
    def __init__(self):
        self.connected = False
        self.closed = False
        self.sent_patterns = []
        self.emitted_patterns = []

    async def connect(self) -> None:
        self.connected = True

    async def close(self) -> None:
        self.closed = True

    async def send(self, pattern: str, data: dict) -> Any:
        self.sent_patterns.append((pattern, data))
        return {"mocked": True, "pattern": pattern, "data": data}

    async def emit(self, pattern: str, data: dict):
        self.emitted_patterns.append((pattern, data))
