from flask import abort, request


def get_body():
    data = request.get_json()
    # json null body counts as empty, any other non-object body is rejected below
    if data is None:
        data = {}
    if not isinstance(data, dict):
        abort(400, "invalid_payload")
    return data


def get_list(data, key):
    value = data.get(key)
    # missing key and json null both return []
    if value is None:
        return []
    if not isinstance(value, list):
        abort(400, "invalid_payload")
    return value


def get_str(data, key, default=None):
    value = data.get(key)
    # missing key and json null both return default
    # callers run their own empty checks and give a precise 400
    if value is None:
        return default
    if not isinstance(value, str):
        abort(400, "invalid_payload")
    return value


def is_number(value, kinds=int):
    # bool is a subclass of int in python: json true/false must not pass as 1/0
    return isinstance(value, kinds) and not isinstance(value, bool)


def get_int(data, key):
    value = data.get(key)
    # missing key and json null both return None
    if value is None:
        return None
    if not is_number(value):
        abort(400, "invalid_payload")
    return value
