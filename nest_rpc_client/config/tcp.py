from dataclasses import dataclass


@dataclass
class TCPConfig:
    host: str
    port: int
