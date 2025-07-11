from dataclasses import dataclass


@dataclass
class NATSConfig:
    servers: list[str]
    response_timeout: int = 10
