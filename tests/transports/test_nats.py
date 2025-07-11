import json
from unittest.mock import AsyncMock, patch

import pytest

from nest_rpc_client.config.nats import NATSConfig
from nest_rpc_client.transports.nats import NATSTransport


@pytest.mark.asyncio
@patch("nest_rpc_client.transports.nats.nats.connect", new_callable=AsyncMock)
async def test_connect(mock_connect):
    fake_client = AsyncMock()
    mock_connect.return_value = fake_client

    config = NATSConfig(["nats://localhost:4222"])
    transport = NATSTransport(config)

    await transport.connect()

    mock_connect.assert_awaited_once_with(config.servers)
    assert transport.client == fake_client


@pytest.mark.asyncio
async def test_close_disconnects_if_connected():
    config = NATSConfig([])
    transport = NATSTransport(config)

    fake_client = AsyncMock()
    fake_client.is_connected = True
    transport.client = fake_client

    await transport.close()
    fake_client.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_close_skips_if_not_connected():
    config = NATSConfig([""])
    transport = NATSTransport(config)

    fake_client = AsyncMock()
    fake_client.is_connected = False
    transport.client = fake_client

    await transport.close()
    fake_client.close.assert_not_awaited()


@pytest.mark.asyncio
@patch("nest_rpc_client.transports.nats.uuid.uuid4")
async def test_send_sends_and_parses_response(mock_uuid4):
    correlation_id = "1234"
    mock_uuid4.return_value = correlation_id

    config = NATSConfig([""])
    transport = NATSTransport(config)

    fake_client = AsyncMock()
    transport.client = fake_client

    response_payload = {"id": correlation_id, "response": {"result": "ok"}}
    fake_msg = AsyncMock()
    fake_msg.data = json.dumps(response_payload).encode("utf-8")
    fake_client.request.return_value = fake_msg

    result = await transport.send("subject", {"x": 1})

    assert result == {"result": "ok"}

    sent_data = json.loads(fake_client.request.call_args.args[1].decode("utf-8"))
    assert sent_data["id"] == correlation_id
    assert sent_data["pattern"] == "subject"
    assert sent_data["data"] == {"x": 1}

    fake_client.request.assert_awaited_once_with(
        "subject",
        fake_client.request.call_args.args[1],
        timeout=config.response_timeout,
    )
