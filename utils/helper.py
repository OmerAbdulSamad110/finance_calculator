from re import sub
from json import dumps, loads


def snakeCase(string: str) -> str:
    return sub(r"\s+", "_", string.lower())


def jsonEncode(data, **kwargs) -> str:
    return dumps(data, **kwargs)


def jsonDecode(data: str):
    return loads(data)
