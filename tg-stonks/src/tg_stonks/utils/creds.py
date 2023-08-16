import os

import dotenv


def load_env_file(env_file_path: str) -> None:
    if not env_file_path:
        raise ValueError("Trying to load `.env` file: got empty str as path")

    if not os.path.exists(env_file_path):
        raise FileNotFoundError(f"`.env` file '{env_file_path}' not found.")

    dotenv.load_dotenv(dotenv_path=env_file_path)


def get_from_env(key: str, env_file_path: str | None = None) -> str | None:
    if env_file_path is not None:
        # take environment variables from .env file
        dotenv.load_dotenv(dotenv_path=env_file_path)

    env_value = os.environ.get(key)
    if env_value is not None:
        return env_value

    # raise error if ENV VAR not set
    raise ValueError(f"Environment variable '{key}' not set.")
