from dataclasses import dataclass


@dataclass
class RabbitMQConfig:
    url: str
    queue: str
