from typing import final

from loguru import logger
from postgrest import APIResponse, APIError
from supabase import Client as SbClient

from database.entity_models import InstrumentType
from database.errors import DbError, DbUserNotFound
from database.protocols import IDatabase


def _expected_exactly_one(resp: APIResponse) -> dict:
    if len(resp.data) == 1:
        return resp.data[0]

    if len(resp.data) == 0:
        raise DbUserNotFound("Query is empty")

    if len(resp.data) > 0:
        logger.trace("<supabase> data integrity error")
        raise DbError(
            "Query expected to return exactly one result,"
            " but returned multiple rows"
        )


class SupabaseDB(IDatabase):
    def __init__(self, url: str, key: str):
        self.sb_client: SbClient = SbClient(
            supabase_url=url,
            supabase_key=key
        )

    def __find_instrument_of_type(
            self,
            type_of_instr: InstrumentType,
            symbol: str,
            data_provider: str
    ) -> APIResponse:

        resp = self.sb_client.table("fin_instruments").select("*").eq(
            "type", type_of_instr).eq(
            "data_provider_code", data_provider).eq(
            "symbol", symbol).execute()

        return resp

    def user_with(self, fields: dict) -> list[dict]:
        query = self.sb_client.table("bot_users").select("*")
        for key, value in fields.items():
            query.eq(key, value)

        resp = query.execute()
        return resp.data

    def user_with_tg_id(self, tg_user_id: int) -> dict:
        resp = self.sb_client.table("bot_users").select("*").eq(
            "tg_user_id", tg_user_id
        ).execute()

        return _expected_exactly_one(resp)

    def settings_of_tg_id(self, tg_user_id: int) -> dict:
        user = self.user_with_tg_id(tg_user_id)
        return user["settings"]

    def find_curr_pair(self, code_from: str, code_to: str, data_provider: str) -> dict:
        resp = self.__find_instrument_of_type(
            InstrumentType.curr_pair,
            f"{code_from}_{code_to}",
            data_provider
        )

        return _expected_exactly_one(resp)

    def find_crypto_pair(self, code_from: str, code_to: str, data_provider: str) -> dict:
        resp = self.__find_instrument_of_type(
            InstrumentType.crypto_pair,
            f"{code_from}_{code_to}",
            data_provider
        )

        return _expected_exactly_one(resp)

    def find_stock_market_instrument(self, symbol: str, data_provider: str) -> dict:
        resp = self.__find_instrument_of_type(
            InstrumentType.sm_instrument,
            symbol,
            data_provider
        )

        return _expected_exactly_one(resp)

    def trackings_with(self, fields: dict) -> list[dict[str, any]]:
        query = self.sb_client.table("tracking").select("*")
        for key, value in fields.items():
            query.eq(key, value)

        resp: APIResponse = query.execute()
        if len(resp.data) == 0:
            raise DbUserNotFound("Query is empty")

        return resp.data

    def add_new_user(self, tg_user_id: int):
        try:
            resp = self.sb_client.table("bot_users").insert(
                {"tg_user_id": tg_user_id}).execute()
            return resp.data[0]

        except APIError as err:
            # TODO: log error
            return None

    def add_instrument(self, instrument_fields: dict):
        try:
            # TODO: does response need additional handling in such cases?
            resp = self.sb_client.table("fin_instruments").insert(
                instrument_fields).execute()
            return resp.data[0]

        except APIError as err:
            # TODO: log error
            return None

    def add_tracking(self, tracking_fields: dict):
        try:
            # TODO: does response need additional handling in such cases?
            resp = self.sb_client.table("tracking").insert(tracking_fields).execute()
            return resp.data[0]

        except APIError as err:
            # TODO: log error
            return None

    def delete_user_by_tg_id(self, tg_user_id: int):
        try:
            resp = self.sb_client.table("bot_users").delete().eq(
                "tg_user_id", tg_user_id
            ).execute()
            return resp.data[0]

        except APIError as err:
            logger.error(f"Failed to delete '{tg_user_id}': {err}")
            return None

    def update_user(self, tg_user_id: int, fields: dict):
        # TODO: do something with response maybe?
        api_resp = self.sb_client.table("bot_users").update(fields).eq("tg_user_id", tg_user_id).execute()
        logger.info(f"User settings updated: {fields}")
        # raise NotImplementedError("Not finished")

    def find_tracking_with(self, fields: dict) -> dict:
        raise NotImplementedError

    def find_instrument_with(self, fields: dict) -> dict:
        raise NotImplementedError

    def add_curr_pair(self):
        raise NotImplementedError

    def add_crypto_pair(self):
        raise NotImplementedError

    def delete_instrument(self):
        raise NotImplementedError

    def delete_tracking(self):
        raise NotImplementedError

    def update_instrument(self):
        raise NotImplementedError
