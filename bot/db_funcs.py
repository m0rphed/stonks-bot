from supabase import create_client, Client as SupabaseClient
from functools import wraps
import creds

# TODO: consider adding more DB options e.g. PocketBase
SupportedDB = SupabaseClient


def with_supabase():
    # TODO: find a way to inject config & then do: `if config.load_env_flag: ...`
    creds.load_env_file("./secret/.env")
    sb_url = creds.get_from_env("SUPABASE_URL")
    # TODO: find a way to inject config & then do: `if config.use_supabase_public: ...`
    sb_key = creds.get_from_env("SUPABASE_SEC_KEY")

    supabase = create_client(sb_url, sb_key)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Validate arguments
            if not isinstance(args[0], SupabaseClient):
                raise ValueError(
                    "First argument must be an instance of `supabase.Client`")

            return func(supabase, *args, **kwargs)

        return wrapper

    return decorator


def with_supabase_config(supabase_url: str, supabase_key: str):
    supabase = create_client(supabase_url, supabase_key)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Validate arguments
            if not isinstance(args[0], SupabaseClient):
                raise ValueError(
                    "First argument must be an instance of `supabase.Client`")

            return func(supabase, *args, **kwargs)

        return wrapper

    return decorator
