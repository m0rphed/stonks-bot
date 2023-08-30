from typing import final, Any

from loguru import logger
from postgrest import APIResponse, APIError, SyncSelectRequestBuilder
from supabase import Client as SbClient

from tg_stonks.database.entity_models import InstrumentType
from tg_stonks.database.errors import (
    DbError,
    DbUserNotFound,
    DbInstrumentNotFound,
    DbTrackingNotFound
)
from tg_stonks.database.protocols import IDatabase


def _expected_exactly_one(resp: APIResponse) -> dict:
    if len(resp.data) == 1:
        return resp.data[0]

    if len(resp.data) > 0:
        logger.trace("[supabase] data integrity error")
        raise DbError(
            "Query expected to return exactly one result,"
            " but returned multiple rows"
        )


def _exactly_one_user(resp: APIResponse, fields: dict = None) -> dict:
    if len(resp.data) == 0:
        raise DbUserNotFound(
            "[supabase] got empty query, but expected exactly 1 match"
            + f"\n-> user fields: {fields}" if fields is not None else ""
        )

    return _expected_exactly_one(resp)


def _exactly_one_instrument(resp: APIResponse, fields: dict = None) -> dict:
    if len(resp.data) == 0:
        raise DbInstrumentNotFound(
            "[supabase] got empty query, but expected exactly 1 match"
            + f"\n-> instrument fields: {fields}" if fields is not None else ""
        )

    return _expected_exactly_one(resp)


def _exactly_one_tracking(resp: APIResponse, fields: dict = None) -> dict:
    if len(resp.data) == 0:
        raise DbTrackingNotFound(
            "[supabase] got empty query, but expected exactly 1 match"
            + f"\n-> tracking fields: {fields}" if fields is not None else ""
        )

    return _expected_exactly_one(resp)


def _build_select_query(query: SyncSelectRequestBuilder, fields: dict[str, Any]) -> SyncSelectRequestBuilder:
    for key, value in fields.items():
        query.eq(key, value)
    return query


@final
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
        # filter by
        # - data provider;
        # - instrument type;
        # => and matching symbol
        resp = self.sb_client.table("fin_instruments").select("*").eq(
            "type", type_of_instr).eq(
            "data_provider_code", data_provider).eq(
            "symbol", symbol).execute()

        return resp

    def users_which(self, fields: dict) -> list[dict]:
        resp: APIResponse = _build_select_query(
            self.sb_client.table("bot_users").select("*"),
            fields
        ).execute()

        return resp.data

    def user_with_tg_id(self, tg_user_id: int) -> dict:
        resp: APIResponse = (
            self.sb_client.table("bot_users")
            .select("*")
            .eq("tg_user_id", tg_user_id)
            .execute()
        )

        return _exactly_one_user(resp)

    def settings_of_tg_user_id(self, tg_user_id: int) -> dict:
        user: dict = self.user_with_tg_id(tg_user_id)
        return user["settings"]

    def find_curr_pair(self, code_from: str, code_to: str, data_provider: str) -> dict:
        resp: APIResponse = self.__find_instrument_of_type(
            InstrumentType.curr_pair,
            f"{code_from}_{code_to}",
            data_provider
        )

        return _exactly_one_instrument(resp)

    def find_crypto_pair(self, code_from: str, code_to: str, data_provider: str) -> dict:
        resp: APIResponse = self.__find_instrument_of_type(
            InstrumentType.crypto_pair,
            f"{code_from}_{code_to}",
            data_provider
        )

        return _exactly_one_instrument(resp)

    def find_stock_market_instrument(self, symbol: str, data_provider: str) -> dict:
        resp: APIResponse = self.__find_instrument_of_type(
            InstrumentType.sm_instrument,
            symbol,
            data_provider
        )

        return _exactly_one_instrument(resp)

    def trackings_with(self, fields: dict) -> list[dict[str, Any]]:
        resp: APIResponse = _build_select_query(
            self.sb_client.table("tracking").select("*"),
            fields
        ).execute()

        return resp.data

    def add_new_user(self, tg_user_id: int):
        try:
            resp: APIResponse = self.sb_client.table("bot_users").insert(
                {"tg_user_id": tg_user_id}
            ).execute()
            return resp.data[0]

        except APIError as err:
            logger.error(
                "[supabase] failed to create new user"
                f" in 'bot_users': {err.message},"
                f"\n-> tg_user_id: {tg_user_id}"
            )
            return None

    def add_instrument(self, instrument_obj: dict):
        try:
            resp: APIResponse = self.sb_client.table("fin_instruments").insert(
                instrument_obj
            ).execute()
            return resp.data[0]

        except APIError as err:
            logger.error(
                "[supabase] failed to insert new instrument"
                f" to 'fin_instruments': {err.message},"
                f"\n-> instrument: {instrument_obj}"
            )
            return None

    def add_tracking(self, tracking_obj: dict):
        try:
            resp: APIResponse = self.sb_client.table("tracking").insert(
                tracking_obj
            ).execute()
            return resp.data[0]

        except APIError as err:
            logger.error(
                "[supabase] failed to insert new tracking order"
                f" to 'tracking': {err.message},"
                f"\n-> tracking: {tracking_obj}"
            )
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
