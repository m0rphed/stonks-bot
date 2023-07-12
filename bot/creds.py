import os
import toml


def get_from_toml(key, toml_path: str = "./secret/keys.toml"):
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


def get_from_env(key):
    env_value = os.environ.get(key)
    if env_value is not None:
        return env_value

    # raise error if ENV VAR not set
    raise ValueError(f"Environment variable '{key}' not set.")


if __name__ == "__main__":
    # Expected default file location: ./secret/keys.toml
    tinkoff = get_from_toml("tinkoff")
    print("key obtained:", tinkoff["token"])
    # print("key obtained:", get_from_env("TOKEN"))
