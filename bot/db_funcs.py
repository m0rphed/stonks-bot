from supabase import create_client, Client as SupabaseClient
from functools import wraps
import creds

# TODO: consider adding more DB options e.g. PocketBase
SupportedDB = SupabaseClient


def get_supabase_client() -> SupabaseClient:
    sb_url = creds.get_from_env("SUPABASE_URL")
    # TODO: find a way to inject config & then do: `if config.use_supabase_public: ...`
    sb_key = creds.get_from_env("SUPABASE_SEC_KEY")
    return create_client(sb_url, sb_key)


def with_supabase(func):
    creds.load_env_file("./secret/.env")
    sb_url = creds.get_from_env("SUPABASE_URL")
    # TODO: find a way to inject config & then do: `if config.use_supabase_public: ...`
    sb_key = creds.get_from_env("SUPABASE_SEC_KEY")
    supabase = create_client(sb_url, sb_key)

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(supabase, *args, **kwargs)

    return wrapper


def with_supabase_config(supabase_url: str, supabase_key: str):
    supabase = create_client(supabase_url, supabase_key)

    def decorator_with_supabase_config(func):
        @wraps(func)
        def wrapper_with_supabase_config(*args, **kwargs):
            return func(supabase, *args, **kwargs)
        return wrapper_with_supabase_config
    return decorator_with_supabase_config

# TODO: consider adding functions that do not relay on specific database
# but can do operations with whatever database provider (that specified by parameter passed to function)
