# nest-rpc-client

[![PyPI](https://img.shields.io/pypi/v/nest-rpc-client?color=blue)](https://pypi.org/project/nest-rpc-client/)
[![Python](https://img.shields.io/pypi/pyversions/nest-rpc-client)](https://pypi.org/project/nest-rpc-client/)

*Async Python client for RPC transport interoperability with NestJS microservices.*
Supports RabbitMQ, Redis, NATS, TCP (and planned support for Kafka, MQTT).

## Features

- Fully async transports
- Pluggable transport architecture
- Compatible with NestJS microservices patterns (send, emit)
- Extras-based installation

## Installation

Install with a specific transport:

```bash
# TCP uses asyncio
pip install "nest-rpc-client[rabbitmq]"
pip install "nest-rpc-client[redis]"
pip install "nest-rpc-client[nats]"
pip install "nest-rpc-client[all]"
```

## Usage

```python
from nest_rpc_client.client import Client
from nest_rpc_client.transports.rabbitmq import RabbitMQTransport
from nest_rpc_client.config.rabbitmq import RabbitMQConfig

transport = RabbitMQTransport(RabbitMQConfig(url="amqp://guest:guest@localhost/", queue="rpc_queue"))

async with Client(transport) as client:
    result = await client.send("get_user", {"id": 123})
    await client.emit("user_created", {"id": 123})
```

You can also use only transport:

```python
from nest_rpc_client.transports.rabbitmq import RabbitMQTransport
from nest_rpc_client.config.rabbitmq import RabbitMQConfig

transport = RabbitMQTransport(RabbitMQConfig(url="amqp://guest:guest@localhost/", queue="rpc_queue"))

await transport.connect()

result = await transport.send("get_user", {"id": 123})
await transport.emit("user_created", {"id": 123})

await transport.close()
```


## Pattern usage with dictionaries

If your pattern is a dictionary (object in js, for example: {cmd: "sum"}), you need to serialize it to a string before using it.
Example:

```python
pattern = json.dumps({"cmd": "sum"}) # '{"cmd": "sum"}'
await client.send(pattern, data)
```


## Custom Transport

`nest-rpc-client` allows you to use your own custom transports. To do this, inherit from the `Transport` base class and implement its abstract methods:

```python
from nest_rpc_client.transport import Transport

class MyCustomTransport(Transport):
    async def connect(self) -> None:
        # Initialize any connections or resources
        ...

    async def close(self) -> None:
        # Clean up resources or close connections
        ...

    async def send(self, pattern: str, data: dict) -> dict:
        # Implement the RPC request (expects a response)
        ...

    async def emit(self, pattern: str, data: dict) -> None:
        # Implement the fire-and-forget event
        ...
```

You can then use your custom transport exactly like the built-in ones:

```python
transport = MyCustomTransport()
async with Client(transport) as client:
    result = await client.send("my_pattern", {"foo": "bar"})
```

## Tests:

This project includes both unit tests and full integration tests.

- Unit tests are included in this repository and can be run with: `pytest`
- Full integration tests are available in a separate repository: [nest-rpc-client-tests](https://github.com/urazmaxambetovserik/nest-rpc-client-tests)

## TODO:

- Implement kafka transport
- Implement mqtt transport
