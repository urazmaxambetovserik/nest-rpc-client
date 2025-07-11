import asyncio
import json
import uuid

import aio_pika

from ..config.rabbitmq import RabbitMQConfig
from ..transport import Transport


class RabbitMQTransport(Transport):
    config: RabbitMQConfig
    connection: aio_pika.abc.AbstractRobustConnection
    channel: aio_pika.abc.AbstractChannel

    def __init__(self, config: RabbitMQConfig):
        self.config = config
        self.channel = None  # type: ignore
        self.connection = None  # type: ignore

    async def connect(self) -> None:
        self.connection = await aio_pika.connect_robust(self.config.url)
        self.channel = await self.connection.channel()

    async def close(self) -> None:
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()

    async def send(self, pattern: str, data: dict) -> dict:
        correlation_id = str(uuid.uuid4())
        reply_queue = await self.channel.declare_queue(exclusive=True)

        body = json.dumps(
            {"id": correlation_id, "pattern": pattern, "data": data}
        ).encode("utf-8")

        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=body,
                correlation_id=correlation_id,
                reply_to=reply_queue.name,
            ),
            routing_key=self.config.queue,
        )

        future = asyncio.get_event_loop().create_future()

        async with reply_queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    if message.correlation_id == correlation_id:
                        response = json.loads(message.body.decode("utf-8"))

                        future.set_result(response["response"])
                        break

        return await future

    async def emit(self, pattern: str, data: dict) -> None:
        body = json.dumps({"pattern": pattern, "data": data}).encode("utf-8")

        await self.channel.default_exchange.publish(
            aio_pika.Message(body=body),
            routing_key=self.config.queue,
        )
