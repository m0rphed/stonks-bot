from loguru import logger
from pyrogram import Client as PyrogramClient

from tg_stonks.bot.formatting import msg_instrument_updated
from tg_stonks.utils.other import ensure_has_key
# TODO: user model paring with errors
# from tg_stonks.database.helpers import to_user
from tg_stonks.database.protocols import IDatabase


async def notify_on_instrument_upd(payload: dict, **kwargs):
    instrument_obj = payload["record"]
    tg_client: PyrogramClient = ensure_has_key(kwargs, "tg_client")
    database: IDatabase = ensure_has_key(kwargs, "database")

    # TODO: here we run multiple queries to determine which user
    #   or users should be notified on instrument price/rate update
    #   -> Instead, it's should be rewritten
    #   using more efficient query - with JOINs (if possible)
    matched_trackings = database.trackings_with({
        "instrument": instrument_obj["id"]
    })

    # every user that have a tracking that
    for tracking_obj in matched_trackings:
        logger.info(f"User with id: '{tracking_obj['tracked_by']}' has a tracking:")
        logger.info(tracking_obj)

        users_who_track = database.users_which({
            "id": tracking_obj["tracked_by"]
        })

        # inner DB id is unique for each user - so it's gotta be exactly one user
        user = users_who_track[0]
        await tg_client.send_message(
            user["tg_user_id"],
            msg_instrument_updated(
                instrument_obj=instrument_obj,
                tracking_obj=tracking_obj
            )
        )
