import secrets


DEFAULT_KEY_LEN = 10


def get_random_key(key_length: int = DEFAULT_KEY_LEN) -> str:
    key = secrets.token_hex(key_length)[:key_length]
    return key
