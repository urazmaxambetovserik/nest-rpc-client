import json
from unittest.mock import AsyncMock, Mock, patch

import pytest

from nest_rpc_client.config.rabbitmq import RabbitMQConfig
from nest_rpc_client.transports.rabbitmq import RabbitMQTransport


class FakeAsyncContextManager:
    def __init__(self, result):
        self._result = result

    async def __aenter__(self):
        return self._result

    async def __aexit__(self, exc_type, exc, tb):
        pass


class FakeProcessContext:
    async def __aenter__(self):
        return None

    async def __aexit__(self, exc_type, exc, tb):
        pass


@pytest.mark.asyncio
async def test_emit_publisher_correct_message():
    config = RabbitMQConfig(url="amqp://localhost:5672", queue="test_queue")
    transport = RabbitMQTransport(config)

    transport.channel = AsyncMock()
    transport.channel.default_exchange.publish = AsyncMock()

    await transport.emit("my_event", {"key": "value"})

    expected_body = json.dumps(
        {"pattern": "my_event", "data": {"key": "value"}}
    ).encode("utf-8")

    transport.channel.default_exchange.publish.assert_awaited_once()
    args, kwargs = transport.channel.default_exchange.publish.call_args

    assert args[0].body == expected_body
    assert kwargs["routing_key"] == config.queue


@pytest.mark.asyncio
@patch(
    "nest_rpc_client.transports.rabbitmq.aio_pika.connect_robust",
    new_callable=AsyncMock,
)
async def test_connect_calls_aio_pika_connect(mock_connect_robust: AsyncMock):
    fake_connection = AsyncMock()
    fake_channel = AsyncMock()

    mock_connect_robust.return_value = fake_connection
    fake_connection.channel.return_value = fake_channel

    config = RabbitMQConfig(url="amqp://localhost:5672", queue="test_queue")
    transport = RabbitMQTransport(config)

    await transport.connect()

    mock_connect_robust.assert_awaited_once_with(config.url)
    fake_connection.channel.assert_awaited_once()

    assert transport.connection == fake_connection
    assert transport.channel == fake_channel


@pytest.mark.asyncio
async def test_close_closes_connection_and_channel():
    config = RabbitMQConfig(url="", queue="")
    transport = RabbitMQTransport(config)

    transport.connection = AsyncMock()
    transport.channel = AsyncMock()

    await transport.close()

    transport.channel.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_close_does_not_fail_if_none():
    config = RabbitMQConfig(url="", queue="")
    transport = RabbitMQTransport(config)

    await transport.close()


@pytest.mark.asyncio
@patch("nest_rpc_client.transports.rabbitmq.uuid.uuid4")
async def test_send_publishes_message_and_receives_reply(mock_uuid4):
    correlation_id = "test-id-123"
    mock_uuid4.return_value = correlation_id

    config = RabbitMQConfig(url="amqp://localhost:5672", queue="test_queue")
    transport = RabbitMQTransport(config)

    fake_channel = AsyncMock()
    fake_exchange = AsyncMock()
    fake_reply_queue = AsyncMock()
    fake_reply_queue.name = "reply-queue-name"
    fake_channel.default_exchange = fake_exchange
    fake_channel.declare_queue.return_value = fake_reply_queue

    transport.channel = fake_channel

    reply_body = json.dumps({"response": {"result": "ok"}}).encode("utf-8")

    fake_message = AsyncMock()
    fake_message.correlation_id = correlation_id
    fake_message.body = reply_body
    fake_message.process = Mock(return_value=FakeProcessContext())

    async def fake_iterator():
        yield fake_message

    fake_reply_queue.iterator = Mock(
        return_value=FakeAsyncContextManager(fake_iterator())
    )

    response = await transport.send("pattern", {"x": 1})

    assert response == {"result": "ok"}

    fake_exchange.publish.assert_awaited_once()
    (msg_arg,) = fake_exchange.publish.call_args[0]
    kwargs = fake_exchange.publish.call_args[1]

    body = json.loads(msg_arg.body.decode())
    assert body["id"] == correlation_id
    assert body["pattern"] == "pattern"
    assert body["data"] == {"x": 1}
    assert msg_arg.reply_to == fake_reply_queue.name
    assert msg_arg.correlation_id == correlation_id
    assert kwargs["routing_key"] == config.queue
