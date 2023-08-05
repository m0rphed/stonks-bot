from postgrest import APIResponse
from returns.result import Result, Success, Failure
from supabase import Client as SbClient

from db import IDatabase, IDatabaseError


class SupabaseDbError(IDatabaseError):
    pass


def _exactly_one_or_none(resp: APIResponse) -> Result[dict, str]:
    if len(resp.data) == 0:
        return Failure("Query is empty")

    if len(resp.data) == 1:
        return Success(resp.data[0])

    if len(resp.data) > 0:
        raise SupabaseDbError(
            "Query expected to return exactly one result,"
            " but returned multiple rows"
        )


class SupabaseDB(IDatabase):
    def __init__(self, url: str, key: str):
        self.sb_client: SbClient = SbClient(
            supabase_url=url,
            supabase_key=key
        )

    def get_settings_of_user(self, tg_user_id: int):
        found_user = self.check_user(tg_user_id)
        if found_user is None:
            raise SupabaseDbError(f"User with tg_user_id: '{tg_user_id}' not found in the database")

        return found_user["settings"]

    def check_user(self, tg_user_id: int):
        resp = self.sb_client.table("bot_users").select("*").eq(
            "tg_user_id", tg_user_id
        ).execute()

        return _exactly_one_or_none(resp)

    def check_curr_pair(self, code_from: str, code_to: str, data_provider: str):
        resp = self.sb_client.table("instruments").select("*").eq(
            "is_curr_pair", True).eq(
            "data_provider", data_provider).eq(
            "code_curr", f"{code_from}_{code_to}").execute()

        return _exactly_one_or_none(resp)

    def check_crypto_pair(self, code_from: str, code_to: str, data_provider: str):
        resp = self.sb_client.table("instruments").select("*").eq(
            "is_crypto_pair", True).eq(
            "data_provider", data_provider).eq(
            "code_curr", f"{code_from}_{code_to}").execute()

        return _exactly_one_or_none(resp)

    def check_instrument(self, ticker: str, data_provider: str):
        resp = self.sb_client.table("instruments").select("*").eq(
            "is_crypto_pair", False).eq(
            "is_curr_pair", False).eq(
            "data_provider", data_provider).eq(
            "ticker", ticker).execute()

        return _exactly_one_or_none(resp)

    def check_instrument_by_fields(self):
        raise NotImplementedError

    def check_tracking(self):
        raise NotImplementedError

    def check_tracking_by_fields(self):
        raise NotImplementedError

    def add_user_by_id(self, tg_user_id: int):
        try:
            resp = self.sb_client.table("bot_users").insert(
                {"tg_user_id": tg_user_id}).execute()
            return resp.data[0]

        except Exception as err:
            # TODO: log error
            return None

    def add_curr_pair(self):
        raise NotImplementedError

    def add_crypto_pair(self):
        raise NotImplementedError

    def add_instrument(self, instrument_fields: dict):
        try:
            # TODO: does response need additional handling in such cases?
            resp = self.sb_client.table("instruments").insert(
                instrument_fields).execute()
            return resp.data[0]

        except Exception as err:
            # TODO: log error
            return None

    def add_tracking(self, tracking_fields: dict):
        try:
            # TODO: does response need additional handling in such cases?
            resp = self.sb_client.table("tracking").insert(tracking_fields).execute()
            return resp.data[0]

        except Exception as err:
            # TODO: log error
            return None

    def delete_user_by_tg_id(self, tg_user_id: int):
        try:
            resp = self.sb_client.table("bot_users").delete().eq(
                "tg_user_id", tg_user_id
            ).execute()
            return resp.data[0]

        except Exception as err:
            # TODO: log error
            return None

    def delete_instrument(self):
        raise NotImplementedError

    def delete_tracking(self):
        raise NotImplementedError

    def update_user(self):
        raise NotImplementedError

    def update_instrument(self):
        raise NotImplementedError

    def add_or_upd_instrument(self):
        raise NotImplementedError
