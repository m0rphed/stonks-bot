import asyncio
import functools

from loguru import logger
from pyrogram import Client, idle, filters
from pyrogram.handlers import MessageHandler

import config
from app_container import AppContainer
from bot_handlers_db_updates import on_instrument_update
from bot_handlers_on_msg import cmd_settings
from db import IDatabase
from db_listener_supabase import SbListener
from db_supabase import SupabaseDB
from provider_alpha_vantage import AlphaVantageAPI

BOT_SESSION_NAME = "stonks-bot"

db: IDatabase = SupabaseDB(
    url=config.SUPABASE_URL,
    key=config.SUPABASE_KEY
)

app = AppContainer(
    data_providers=[
        AlphaVantageAPI(key=config.ALPHA_VANTAGE_KEY)
    ],
    db=db
)


async def start_listener():
    lis = SbListener(
        sb_id=config.SUPABASE_ID,
        sb_key=config.SUPABASE_KEY,
    )

    await lis.set_up("fin_instruments")
    logger.info(f"<listener> socket and channel set up: {lis.ready_to_listen}")

    cl_for_updates = Client(
        f"{BOT_SESSION_NAME}_upd-listener",
        api_id=config.TELEGRAM_API_ID,
        api_hash=config.TELEGRAM_API_HASH,
        bot_token=config.TELEGRAM_BOT_TOKEN
    )

    lis.add_callback(
        "UPDATE", on_instrument_update, tg_client=cl_for_updates, database=db
    )

    await cl_for_updates.start()
    await asyncio.gather(lis.start_listening(), idle())
    await cl_for_updates.stop()


async def start_main_bot():
    cl_main = Client(
        f"{BOT_SESSION_NAME}_main",
        api_id=config.TELEGRAM_API_ID,
        api_hash=config.TELEGRAM_API_HASH,
        bot_token=config.TELEGRAM_BOT_TOKEN
    )

    handle_settings = MessageHandler(
        functools.partial(
            cmd_settings,
            app=app),
        filters.command("settings")
    )

    cl_main.add_handler(handle_settings)

    await cl_main.start()
    await idle()
    await cl_main.stop()


async def main():
    await asyncio.gather(
        start_listener(),
        start_main_bot()
    )


if __name__ == "__main__":
    logger.info("Starting app main...")
    asyncio.run(main())
    logger.info("Finishing app main...")
