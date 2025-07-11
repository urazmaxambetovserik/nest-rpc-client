import json
from unittest.mock import AsyncMock, Mock, patch

import pytest

from nest_rpc_client.config.redis import RedisConfig
from nest_rpc_client.transports.redis import RedisTransport


class FakeListen:
    def __init__(self, items: list):
        self._items = iter(items)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self._items)
        except StopIteration:
            raise StopAsyncIteration


@pytest.mark.asyncio
@patch("nest_rpc_client.transports.redis.Redis")
async def test_connect(mock_redis):
    fake_client = AsyncMock()
    mock_redis.return_value = fake_client

    config = RedisConfig("", 6379)
    transport = RedisTransport(config)

    await transport.connect()

    mock_redis.assert_called_once_with(host="", port=6379)
    assert transport.client == fake_client


@pytest.mark.asyncio
async def test_close_closes_client_if_exists():
    config = RedisConfig("", 6379)
    transport = RedisTransport(config)

    transport.client = AsyncMock()
    await transport.close()

    transport.client.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_close_does_not_fail_if_client_is_done():
    config = RedisConfig("", 6379)
    transport = RedisTransport(config)

    transport.client = None  # type: ignore
    await transport.close()


@pytest.mark.asyncio
async def test_emit_publishes_correct_message():
    config = RedisConfig("", 1)
    transport = RedisTransport(config)

    fake_client = AsyncMock()
    transport.client = fake_client

    await transport.emit("pattern", {"key": "value"})

    expected_body = json.dumps({"pattern": "pattern", "data": {"key": "value"}})
    fake_client.publish.assert_awaited_once_with("pattern", expected_body)


@pytest.mark.asyncio
@patch("nest_rpc_client.transports.redis.uuid.uuid4")
async def test_send_publishes_and_listens_for_response(mock_uuid4):
    correlation_id = "1234"
    mock_uuid4.return_value = correlation_id

    config = RedisConfig("", 1)
    transport = RedisTransport(config)

    fake_client = AsyncMock()
    transport.client = fake_client

    fake_pubsub = AsyncMock()
    fake_client.pubsub = Mock(return_value=fake_pubsub)

    expected_response = {"foo": "bar"}
    response_message = {
        "type": "message",
        "data": json.dumps({"id": correlation_id, "response": expected_response}),
    }

    async def fake_listen():
        yield response_message

    fake_pubsub.listen = Mock(return_value=fake_listen())

    fake_pubsub.subscribe = AsyncMock()
    fake_pubsub.unsubscribe = AsyncMock()
    fake_pubsub.close = AsyncMock()

    result = await transport.send("pattern", {"x": 123})

    assert result == expected_response

    sent_data = json.loads(fake_client.publish.call_args.args[1])
    assert sent_data["id"] == correlation_id
    assert sent_data["pattern"] == "pattern"
    assert sent_data["data"] == {"x": 123}

    fake_pubsub.subscribe.assert_awaited_once_with("pattern.reply")
    fake_pubsub.unsubscribe.assert_awaited_once_with("pattern.reply")
    fake_pubsub.close.assert_awaited_once()
