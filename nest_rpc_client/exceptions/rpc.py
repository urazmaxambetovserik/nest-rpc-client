from dataclasses import dataclass
from typing import Any


@dataclass
class RpcException(Exception):
    err: Any
