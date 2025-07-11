# nest-rpc-client

*Async Python client for RPC transport interoperability with NestJS microservices.*
Supports RabbitMQ, Redis, NATS (and planned support for Kafka, MQTT).

## Features

- Fully async transports
- Pluggable transport architecture
- Compatible with NestJS microservices patterns (send, emit)
- Extras-based installation

## Installation

Install with a specific transport:

```bash
pip install "nest-rpc-client[rabbitmq]"
pip install "nest-rpc-client[redis]"
pip install "nest-rpc-client[nats]"
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

- Implement tcp transport
- Implement kafka transport
- Implement mqtt transport
