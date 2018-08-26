def to_str(bytes_or_str, errors=None):
    if isinstance(bytes_or_str, bytes):
        value = bytes_or_str.decode("utf-8", errors=errors)
    else:
        value = bytes_or_str
    return value