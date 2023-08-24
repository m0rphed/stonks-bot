from typing import Any


def ensure_has_key(the_kwargs: dict, key: str) -> Any:
    arg_v = the_kwargs.get(key)
    if arg_v is None:
        raise RuntimeError(
            "Required arguments not passed:"
            f" argument '{key}' not found"
            " in function kwargs"
        )
    return arg_v
