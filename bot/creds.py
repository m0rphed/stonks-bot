import os
import toml
from dotenv import load_dotenv


def get_from_toml(key: str, toml_path: str = "./secret/keys.toml"):
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


def get_from_env(key: str, env_file_path: str | None = None):
    if env_file_path is not None:
        # take environment variables from .env file
        load_dotenv(dotenv_path=env_file_path)

    env_value = os.environ.get(key)
    if env_value is not None:
        return env_value

    # raise error if ENV VAR not set
    raise ValueError(f"Environment variable '{key}' not set.")


if __name__ == "__main__":
    # Expected default file location: ./secret/keys.toml
    tinkoff = get_from_toml("tinkoff")
    print("> Tinkoff key obtained:", tinkoff["token"])
    print("> Alpha vantage api key:", get_from_toml("alpha-vantage")["token"])
    # print("key obtained:", get_from_env("SOME_TOKEN"))
    print("> Got from .env file:", get_from_env("TINKOFF_TOKEN", env_file_path="./secret/.env"))
    print("> Got from .env file:", get_from_env("TELEGRAM_API_API_ID", env_file_path="./secret/.env"))
    