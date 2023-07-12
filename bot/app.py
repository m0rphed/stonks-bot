from dataclasses import dataclass
import os
import toml


@dataclass(frozen=True)
class FromFileTOML:
    key: str
    toml: tuple = ("secret", "keys.toml")


@dataclass(frozen=True)
class FromEvnVar:
    key: str


ReadOptions = FromFileTOML | FromEvnVar


def read_key(read_from: ReadOptions):
    match read_from:
        case FromFileTOML(secret_key, toml_path):
            # get the file path
            file_path = os.path.join(*toml_path)
            file_path = os.path.join(os.getcwd(), file_path)
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"TOML file '{file_path}' not found.")

            # read keys to memory
            secrets = toml.load(file_path)
            if secret_key not in secrets:
                raise ValueError(
                    f"'{secret_key}' not found in the TOML file.")

            return secrets[secret_key]  # return specified secret key

        case FromEvnVar(env_name):
            env_value = os.environ.get(env_name)
            if env_value is not None:
                return env_value

            # raise error if ENV VAR not set
            raise ValueError(f"Environment variable '{env_name}' not set.")

        case _:
            raise ValueError("Invalid `read_from` parameter.")


if __name__ == "__main__":
    # Expected default file location: ./secret/keys.toml
    read_from = FromFileTOML(key="tinkoff")
    data = read_key(read_from)
    print("key obtained:", data["token"])
