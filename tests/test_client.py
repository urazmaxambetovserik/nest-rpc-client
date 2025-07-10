import pytest

from nest_rpc_client.client import Client
from nest_rpc_client.transports.mock import MockTransport


@pytest.mark.asyncio
async def test_client_send_and_emit():
    transport = MockTransport()
    client = Client(transport)

    async with client as c:
        result = await c.send("sum", {"a": 1, "b": 2})
        assert result["mocked"] is True
        assert result["pattern"] == "sum"
        assert result["data"] == {"a": 1, "b": 2}

        await c.emit("log", {"msg": "hello"})

    assert transport.connected is True
    assert transport.closed is True
    assert transport.sent_patterns == [("sum", {"a": 1, "b": 2})]
    assert transport.emitted_patterns == [("log", {"msg": "hello"})]
