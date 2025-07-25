import asyncio
import json
import uuid

from redis.asyncio import Redis

from ..config.redis import RedisConfig
from ..transport import Transport
from ..utils.parse_response import parse_response


class RedisTransport(Transport):
    config: RedisConfig
    client: Redis

    def __init__(self, config: RedisConfig):
        self.config = config

    async def connect(self) -> None:
        self.client = Redis(host=self.config.host, port=self.config.port)

    async def close(self) -> None:
        if hasattr(self, "client") and self.client:
            await self.client.aclose()

    async def send(self, pattern: str, data: dict) -> dict:
        correlation_id = str(uuid.uuid4())
        reply_channel = f"{pattern}.reply"

        message = json.dumps({"id": correlation_id, "pattern": pattern, "data": data})

        pubsub = self.client.pubsub()
        await pubsub.subscribe(reply_channel)

        future = asyncio.get_event_loop().create_future()

        async def listener():
            try:
                async for msg in pubsub.listen():
                    if msg["type"] != "message":
                        continue

                    response_body = json.loads(msg["data"])

                    if response_body.get("id") != correlation_id:
                        continue

                    future.set_result(parse_response(response_body))
                    break
            except Exception as e:
                future.set_exception(e)
            finally:
                await pubsub.unsubscribe(reply_channel)
                await pubsub.aclose()

        asyncio.create_task(listener())
        await self.client.publish(pattern, message)

        return await future

    async def emit(self, pattern: str, data: dict) -> None:
        message = json.dumps({"pattern": pattern, "data": data})
        await self.client.publish(pattern, message)
