from typing import final

from loguru import logger
from postgrest import APIResponse, APIError
from returns.result import Result, Success, Failure
from supabase import Client as SbClient

from db import IDatabase, IDatabaseError
from db_helpers import to_user_entity, to_instrument
from models import UserEntity, InstrumentType, InstrumentEntity


@final
class SupabaseDbError(IDatabaseError):
    pass


def _expected_exactly_one(resp: APIResponse) -> Result[dict, any]:
    if len(resp.data) == 0:
        return Failure("Query is empty")

    if len(resp.data) == 1:
        return Success(resp.data[0])

    if len(resp.data) > 0:
        logger.trace("<supabase> data integrity error")
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

    def __find_instrument_of_type(
            self,
            type_of_instr: InstrumentType,
            symbol: str,
            data_provider: str
    ) -> APIResponse:

        resp = self.sb_client.table("fin_instruments").select("*").eq(
            "type", type_of_instr).eq(
            "data_provider", data_provider).eq(
            "symbol", symbol).execute()

        return resp

    def find_user_by_tg_id(self, tg_user_id: int) -> Result[UserEntity, any]:
        resp = self.sb_client.table("bot_users").select("*").eq(
            "tg_user_id", tg_user_id
        ).execute()

        found_user: Result = to_user_entity(_expected_exactly_one(resp))
        if isinstance(found_user, Failure):
            logger.info(f"<supabase> User not found: {found_user.failure()}; 'tg_user_id': {tg_user_id}")

        return found_user

    def get_settings_of_user(self, tg_user_id: int) -> Result[dict, any]:
        res = self.find_user_by_tg_id(tg_user_id)
        if isinstance(res, Failure):
            logger.error(f"<supabase> Error getting settings of user: '{tg_user_id}'")
            return Failure(res.failure())

        return Success(res.unwrap().settings)

    def find_curr_pair(self, code_from: str, code_to: str, data_provider: str) -> Result[InstrumentEntity, any]:
        resp = self.__find_instrument_of_type(
            InstrumentType.curr_pair,
            f"{code_from}_{code_to}",
            data_provider
        )

        return to_instrument(_expected_exactly_one(resp))

    def find_crypto_pair(self, code_from: str, code_to: str, data_provider: str) -> Result[InstrumentEntity, any]:
        resp = self.__find_instrument_of_type(
            InstrumentType.crypto_pair,
            f"{code_from}_{code_to}",
            data_provider
        )

        return to_instrument(_expected_exactly_one(resp))

    def find_stock_market_instrument(self, ticker: str, data_provider: str) -> Result[InstrumentEntity, any]:
        resp = self.__find_instrument_of_type(
            InstrumentType.sm_instrument,
            ticker,
            data_provider
        )

        return to_instrument(_expected_exactly_one(resp))

    def find_instrument_by_fields(self, fields: dict) -> Result[InstrumentEntity, any]:
        raise NotImplementedError

    def find_tracking(self):
        raise NotImplementedError

    def find_tracking_by_fields(self):
        raise NotImplementedError

    def add_user_by_tg_id(self, tg_user_id: int):
        try:
            resp = self.sb_client.table("bot_users").insert(
                {"tg_user_id": tg_user_id}).execute()
            return resp.data[0]

        except APIError as err:
            # TODO: log error
            return None

    def add_curr_pair(self):
        raise NotImplementedError

    def add_crypto_pair(self):
        raise NotImplementedError

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

    def delete_instrument(self):
        raise NotImplementedError

    def delete_tracking(self):
        raise NotImplementedError

    def update_user(self, tg_user_id: int, fields: dict):
        # TODO: do something with response maybe?
        api_resp = self.sb_client.table("bot_users").update(fields).eq("tg_user_id", tg_user_id).execute()
        logger.info(f"User settings updated: {fields}")
        # raise NotImplementedError("Not finished")

    def update_instrument(self):
        raise NotImplementedError

    def add_or_upd_instrument(self):
        raise NotImplementedError
