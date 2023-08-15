from typing import Any

from loguru import logger
from pyrogram import Client as PyrogramClient

from database import helpers
from database.protocol import IDatabase


def _get_or_raise(the_kwargs: dict, key: str) -> Any:
    found = the_kwargs.get(key)
    if found is None:
        raise RuntimeError(
            "Could not handle database updates:"
            f" argument '{key}' not specified"
            " to callback function"
        )
    return found


async def on_instrument_update(payload: dict, **kwargs):
    instr_obj = payload["record"]
    tg_client: PyrogramClient = _get_or_raise(kwargs, "tg_client")
    idb: IDatabase = _get_or_raise(kwargs, "database")
    matched_tracking: list[dict] = idb.trackings_with({"instrument": instr_obj["id"]})
    for trk in matched_tracking:
        db_user_id = trk["tracked_by"]
        logger.info(f"Inner database user id: {db_user_id}\n\t=> tracking: {trk}")

        user_obj = idb.user_with({"id": db_user_id})
        user = db_helpers.to_user(user_obj)
        logger.info(f"telegram user id: {user.tg_user_id}\n\t=> of user: {user.id}")

        await tg_client.send_message(user.tg_user_id, f"current price: {instr_obj['price']}\n\n" + str(trk))
