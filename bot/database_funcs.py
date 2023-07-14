from supabase import create_client, Client as SupabaseClient
import creds

SupportedDB = SupabaseClient


def supabase_client_init(load_env_file: bool = False) -> SupabaseClient:
    if load_env_file:
        creds.load_env_file("./secret/.env")

    client: SupabaseClient = create_client(
        creds.get_from_env("SUPABASE_URL"),
        # TODO: use PUBLIC supabase key if possible (now using service_role)
        creds.get_from_env("SUPABASE_SEC_KEY")
    )

    return client


def check_user(user: str):
    pass


def sign_in():
    pass
