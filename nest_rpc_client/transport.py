from abc import ABC, abstractmethod
from typing import Any


class Transport(ABC):
    @abstractmethod
    async def connect(self) -> None:
        """
        Estabilish connection to the underlying transport (e.g. broker, socket)
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """
        Gracefully close the transport connection.
        """
        pass

    @abstractmethod
    async def send(self, pattern: str, data: dict) -> Any:
        """
        RPC-style request/response.
        Client expects a single reply
        """
        pass

    @abstractmethod
    async def emit(self, pattern: str, data: dict) -> None:
        """
        Fire-and-forget event.
        Client does not expect a reply.
        """
        pass
