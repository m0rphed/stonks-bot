import os

import dotenv
import toml

__DEFAULT_TOML_PATH: str = "./secret/keys.toml"


def get_from_toml(key: str, toml_path: str = __DEFAULT_TOML_PATH) -> str | None:
    # get the file path
    file_path = os.path.join(toml_path)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"TOML file '{file_path}' not found.")

    # read keys to memory
    secrets = toml.load(file_path)
    if key not in secrets:
        raise ValueError(
            f"'{key}' not found in the TOML file.")

    return secrets[key]  # return specified secret key


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


if __name__ == "__main__":
    # TODO: write some tests
    print("maybe some tests here, huh?")
    pass
