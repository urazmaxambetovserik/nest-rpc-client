import json
from unittest.mock import AsyncMock, Mock, patch

import pytest

from nest_rpc_client.config.tcp import TCPConfig
from nest_rpc_client.transports.tcp import TCPTransport


@pytest.mark.asyncio
@patch("nest_rpc_client.transports.tcp.asyncio.open_connection", new_callable=AsyncMock)
async def test_connect(mock_open_connection):
    fake_reader = AsyncMock()
    fake_writer = AsyncMock()
    mock_open_connection.return_value = (fake_reader, fake_writer)

    config = TCPConfig("localhost", 3002)
    transport = TCPTransport(config)

    await transport.connect()

    mock_open_connection.assert_awaited_once_with(config.host, config.port)
    assert transport.reader == fake_reader
    assert transport.writer == fake_writer


@pytest.mark.asyncio
async def test_close_calls_writer_close():
    config = TCPConfig("localhost", 3002)
    transport = TCPTransport(config)

    fake_reader = AsyncMock()
    fake_writer = AsyncMock()

    fake_writer.close = Mock()
    fake_writer.wait_closed = AsyncMock()

    transport.reader = fake_reader
    transport.writer = fake_writer

    await transport.close()

    fake_writer.close.assert_called_once()
    fake_writer.wait_closed.assert_awaited_once()


@pytest.mark.asyncio
async def test_emit_sends_correct_format():
    config = TCPConfig("localhost", 3002)
    transport = TCPTransport(config)

    fake_reader = AsyncMock()
    fake_writer = AsyncMock()
    fake_writer.write = Mock()

    transport.reader = fake_reader
    transport.writer = fake_writer

    await transport.emit("pattern", {"foo": "bar"})

    sent_bytes = fake_writer.write.call_args.args[0]
    sent_str = sent_bytes.decode()

    length_str, json_str = sent_str.split("#", 1)
    assert int(length_str) == len(json_str)

    payload = json.loads(json_str)
    assert payload["pattern"] == "pattern"
    assert payload["data"] == {"foo": "bar"}

    fake_writer.drain.assert_awaited_once()


@pytest.mark.asyncio
@patch("uuid.uuid4")
async def test_send_sends_and_receives_response(mock_uuid4):
    correlation_id = "test-id"
    mock_uuid4.return_value = correlation_id

    config = TCPConfig("localhost", 3002)
    transport = TCPTransport(config)

    fake_reader = AsyncMock()
    fake_writer = AsyncMock()
    fake_writer.write = Mock()

    transport.reader = fake_reader
    transport.writer = fake_writer

    response_payload = json.dumps({"id": correlation_id, "response": {"result": "ok"}})
    server_message = f"{len(response_payload)}#{response_payload}"
    fake_reader.read = AsyncMock(side_effect=[server_message.encode(), b""])

    result = await transport.send("pattern", {"foo": "bar"})

    assert result == {"result": "ok"}

    sent_bytes = fake_writer.write.call_args.args[0]
    sent_str = sent_bytes.decode()
    length_str, json_str = sent_str.split("#", 1)
    assert int(length_str) == len(json_str)

    sent_payload = json.loads(json_str)
    assert sent_payload["pattern"] == "pattern"
    assert sent_payload["data"] == {"foo": "bar"}
    assert sent_payload["id"] == correlation_id

    fake_writer.drain.assert_awaited()
