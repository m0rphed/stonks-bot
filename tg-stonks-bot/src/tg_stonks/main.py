import asyncio

from loguru import logger
from pyrogram import Client, idle

import tg_stonks.config as config

import tg_stonks.bot.handlers_callbacks as on_cb_query
import tg_stonks.bot.handlers_messages as on_msg
from tg_stonks.bot.app_container import AppContainer
from tg_stonks.bot.handlers_db_updates import on_instrument_update

from tg_stonks.database.protocols import IDatabase

from tg_stonks.impl.alpha_vantage_provider import AlphaVantageAPI
from tg_stonks.impl.supabase_database import SupabaseDB
from tg_stonks.impl.supabase_listener import SupabaseListener

BOT_SESSION_NAME = "stonks-tg-stonks-bot"

db: IDatabase = SupabaseDB(
    url=config.SUPABASE_URL,
    key=config.SUPABASE_KEY
)

app = AppContainer(
    data_providers=[
        AlphaVantageAPI(key=config.ALPHA_VANTAGE_KEY)
    ],
    database=db
)


async def start_listener():
    lis = SupabaseListener(
        sb_id=config.SUPABASE_ID,
        sb_key=config.SUPABASE_KEY,
    )

    await lis.set_up("fin_instruments")
    logger.info(f"<listener> socket and channel set up: {lis.ready_to_listen}")

    c_for_listener = Client(
        f"{BOT_SESSION_NAME}_upd-listener",
        api_id=config.TELEGRAM_API_ID,
        api_hash=config.TELEGRAM_API_HASH,
        bot_token=config.TELEGRAM_BOT_TOKEN
    )

    lis.add_callback(
        "UPDATE", on_instrument_update,
        tg_client=c_for_listener,
        database=db
    )

    await c_for_listener.start()
    await asyncio.gather(lis.start_listening(), idle())
    await c_for_listener.stop()


async def start_main_bot():
    c_main = Client(
        f"{BOT_SESSION_NAME}_main",
        api_id=config.TELEGRAM_API_ID,
        api_hash=config.TELEGRAM_API_HASH,
        bot_token=config.TELEGRAM_BOT_TOKEN
    )

    for command_handler in on_msg.get_commands(app):
        c_main.add_handler(command_handler)

    for cb_query_handler in on_cb_query.get_callbacks_handlers(app):
        c_main.add_handler(cb_query_handler)

    await c_main.start()
    await idle()
    await c_main.stop()


async def main():
    await asyncio.gather(
        start_listener(),
        start_main_bot()
    )


if __name__ == "__main__":
    logger.info("Starting app main...")
    asyncio.run(main())
    logger.info("Finishing app main...")
