import pytest

from nest_rpc_client.exceptions.rpc import RpcException
from nest_rpc_client.utils.parse_response import parse_response


def test_parse_response_success():
    response = {"id": "abc-123", "response": {"user_id": 1, "name": "42"}}

    result = parse_response(response)

    assert result == {"user_id": 1, "name": "42"}


def test_parse_response_with_error():
    response = {"id": "abc-123", "err": {"message": "Not found", "code": 404}}

    with pytest.raises(RpcException) as exc_info:
        parse_response(response)

    assert isinstance(exc_info.value, RpcException)
    assert exc_info.value.err == {"message": "Not found", "code": 404}
