from supabase import Client as SupabaseClient
from models import BotUserEntity, InstrumentEntity, TrackingEntity
from db_funcs import with_supabase, with_supabase_config


@with_supabase
def check_user(supabase: SupabaseClient, tg_user_id: int) -> BotUserEntity | None:
    resp = supabase.table("bot_users").select("*"
        ).eq("tg_user_id", tg_user_id).execute()

    if len(resp.data) > 0:
        if len(resp.data) == 1:
            return BotUserEntity.parse_obj(resp.data[0])

        # TODO: impl. & raise something like `DBError(...)`
        raise Exception(
            f"DB have multiple users with the same `tg_bot_id`:"
            f" {tg_user_id} -> data must be corrupted")

    return None


@with_supabase
def check_curr_pair(supabase: SupabaseClient, code_from: str, code_to: str, data_provider: str) -> InstrumentEntity | None:
    resp = supabase.table("instruments").select("*"
        ).eq("is_curr_pair", True
        ).eq("data_provider", data_provider
        ).eq("code_curr", f"{code_from}_{code_to}").execute()

    if len(resp.data) > 0:
        if len(resp.data) == 1:
            return InstrumentEntity.parse_obj(resp.data[0])

        # TODO: impl. & raise something like `DBError(...)`
        raise Exception(
            f"DB have multiple currency pair with the same `code_curr`:"
            f" {code_from}_{code_to} -> data must be corrupted")

    raise None


@with_supabase
def check_crypto_pair(supabase: SupabaseClient, code_from: str, code_to: str, data_provider: str) -> InstrumentEntity | None:
    resp = supabase.table("instruments").select("*"
        ).eq("is_crypto_pair", True
        ).eq("data_provider", data_provider
        ).eq("code_curr", f"{code_from}_{code_to}").execute()

    if len(resp.data) > 0:
        if len(resp.data) == 1:
            return InstrumentEntity.parse_obj(resp.data[0])

        # TODO: impl. & raise something like `DBError(...)`
        raise Exception(
            f"DB have multiple crypto currency pair with the same `code_curr`:"
            f" {code_from}_{code_to} -> data must be corrupted")

    raise None


@with_supabase
def check_instrument_by_figi(supabase: SupabaseClient, code_figi: str, data_provider: str) -> InstrumentEntity | None:
    resp = supabase.table("instruments").select("*"
        ).eq("is_crypto_pair", False    # TODO: does adding constrains in such case improve perf.? 
        ).eq("is_curr_pair", False      # TODO: does adding constrains in such case improve perf.?
        ).eq("data_provider", data_provider
        ).eq("code_figi", code_figi).execute()

    if len(resp.data) > 0:
        if len(resp.data) == 1:
            return InstrumentEntity.parse_obj(resp.data[0])

        # TODO: impl. & raise something like `DBError(...)`
        raise Exception(
            f"DB have multiple instruments with the same `code_figi`:"
            f" {code_figi} (`data_provider`: {data_provider})"
            "-> data must be corrupted")

    raise None


@with_supabase
def check_instrument_by_ticker(supabase: SupabaseClient, ticker: str, data_provider: str) -> InstrumentEntity | None:
    resp = supabase.table("instruments").select("*"
        ).eq("is_crypto_pair", False    # TODO: does adding constrains in such case improve perf.? 
        ).eq("is_curr_pair", False      # TODO: does adding constrains in such case improve perf.?
        ).eq("data_provider", data_provider
        ).eq("ticker", ticker).execute()

    if len(resp.data) > 0:
        if len(resp.data) == 1:
            return InstrumentEntity.parse_obj(resp.data[0])

        # TODO: impl. & raise something like `DBError(...)`
        raise Exception(
            f"DB have multiple instruments with the same `ticker`:"
            f" {ticker} (`data_provider`: {data_provider})"
            "-> data must be corrupted")

    raise None


@with_supabase
def add_user_by_id(supabase: SupabaseClient, tg_user_id: int) -> dict | None:
    try:
        # TODO: does response need additional handling in such cases?
        resp = supabase.table("bot_users").insert(
            {"tg_user_id": tg_user_id}).execute()
        return resp.data[0]

    except Exception as e:
        # TODO: log error
        return None


@with_supabase
def add_user(supabase: SupabaseClient, bot_user_fields: dict) -> dict | None:
    try:
        # TODO: does response need additional handling in such cases?
        resp = supabase.table("bot_users").insert(
            bot_user_fields).execute()
        return resp.data[0]

    except Exception as e:
        # TODO: log error
        return None


@with_supabase
def add_instrument(supabase: SupabaseClient, instrument_fields: dict) -> dict | None:
    try:
        # TODO: does response need additional handling in such cases?
        resp = supabase.table("instruments").insert(
            instrument_fields).execute()
        return resp.data[0]

    except Exception as e:
        # TODO: log error
        return None


@with_supabase
def add_tracking(supabase: SupabaseClient, tracking_fields: dict) -> dict | None:
    try:
        # TODO: does response need additional handling in such cases?
        resp = supabase.table("tracking").insert(tracking_fields).execute()
        return resp.data[0]

    except Exception as e:
        # TODO: log error
        return None


@with_supabase
def get_trackings(supabase: SupabaseClient, tracked_by_user: int) -> list[TrackingEntity] | None:
    resp = supabase.table("tracking"
                          ).select("*, bot_users(*)"
                                   ).eq("bot_users.tg_user_id", tracked_by_user).execute()
    print(resp.data)
    raise NotImplementedError("Implementation not ready")
    # return None


def _test():
    pass


if __name__ == "__main__":
    _test()
