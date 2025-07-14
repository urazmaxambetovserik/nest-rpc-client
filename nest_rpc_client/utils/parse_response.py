from ..exceptions.rpc import RpcException


def parse_response(response: dict):
    if "err" in response:
        raise RpcException(response["err"])
    return response["response"]
