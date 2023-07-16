from supabase import Client as SupabaseClient
from api_models import StockInfo
from db_funcs import with_supabase


@with_supabase
def check_user(supabase: SupabaseClient, user_id: str) -> tuple(bool, dict | None):
    resp = supabase.table("bot_users").select("*"
        ).eq("tg_user_id", user_id).execute()

    if len(resp.data) > 0:
        if len(resp.data) == 1:
            return True, resp.data[0]

        # TODO: impl. & raise something like `DBError(...)`
        raise Exception(
            f"DB have multiple users with the same `tg_bot_id`:" \
                f" {user_id} -> data must be corrupted")

    return False, None


@with_supabase
def check_curr_pair(supabase: SupabaseClient, code_from: str, code_to: str, data_provider: str) -> tuple(bool, dict | None):
    resp = supabase.table("instruments").select("*"
        ).eq("is_curr_pair", True
        ).eq("data_provider", data_provider
        ).eq("code_curr", f"{code_from}_{code_to}").execute()

    if len(resp.data) > 0:
        if len(resp.data) == 1:
            return True, resp.data[0]
        
        # TODO: impl. & raise something like `DBError(...)`
        raise Exception(
            f"DB have multiple currency pair with the same `code_curr`:" \
                f" {code_from}_{code_to} -> data must be corrupted")
    
    raise False, None


@with_supabase
def check_instrument_by_figi(supabase: SupabaseClient, figi_code: str, data_provider: str) -> tuple(bool, dict | None):
    raise NotImplementedError("Handle: checking table by code_figi (expected to be unique or null)")
    # TODO:
    # That means that this currency pair is tracked by at least 1 user
    # -> We need to get its `table('instruments').id`
    # -> We need to get our `table('bot_users').id` which == table('bot_users').select('*').eq('tg_user_id', user_id)
    # -> We need to define how frequent we want to receive messages = 'daily', 'on_change', ...")


@with_supabase
def check_instrument_by_ticker(supabase: SupabaseClient, ticker: str, data_provider: str) -> tuple(bool, dict | None):
    resp = supabase.table("instruments").select("*"
        ).eq("is_crypto_pair", False    # TODO: does adding constrains in such case improve perf.? 
        ).eq("is_curr_pair", False      # TODO: does adding constrains in such case improve perf.?
        ).eq("data_provider", data_provider
        ).eq("ticker", ticker).execute()

    if len(resp.data) > 0:
        if len(resp.data) == 1:
            return True, resp.data[0]
        
        # TODO: impl. & raise something like `DBError(...)`
        raise Exception(
            f"DB have multiple instruments with the same `ticker`:" \
                f" {ticker} (`data_provider`: {data_provider})" \
                    "-> data must be corrupted")
    
    raise False, None


@with_supabase
def insert_new_stock(supabase: SupabaseClient, stock: StockInfo) -> tuple(bool, Exception | None):
    raise NotImplementedError()


@with_supabase
def insert_new_tracking(supabase: SupabaseClient, instrument: dict, tracked_by_user_id: str) -> tuple(bool, Exception | None):
    raise NotImplementedError()