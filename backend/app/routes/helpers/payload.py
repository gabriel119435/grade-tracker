from flask import abort, request


def get_body():
    data = request.get_json() or {}
    if not isinstance(data, dict):
        abort(400, "invalid_payload")
    return data


def get_str(data, key, default=None):
    value = data.get(key, default)
    if value is None:
        return None
    if not isinstance(value, str):
        abort(400, "invalid_payload")
    return value


def get_int(data, key):
    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        abort(400, "invalid_payload")
    return value


def get_list(data, key):
    value = data.get(key, [])
    if not isinstance(value, list):
        abort(400, "invalid_payload")
    return value
