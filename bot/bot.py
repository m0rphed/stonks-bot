from pyrogram import Client as PyrogramClient
from pyrogram import enums, filters
from pyrogram.types import CallbackQuery, Message
from returns.result import Failure, Success

import config
from bot_helpers import filter_cb_data_starts, confirmation_markup
from db import IDatabase
from db_supabase import SupabaseDB
from formatting import msg_error, msg_warning, msg_ok
from models import SearchQueryRes
from provider_alpha_vantage import AlphaVantageAPI
from tg_bot import TelegramCreds, TgBot

db: IDatabase = SupabaseDB(
    url=config.SUPABASE_URL,
    key=config.SUPABASE_KEY
)

# set telegram client credentials
tg_creds = TelegramCreds(
    api_id=int(config.TELEGRAM_API_ID),
    api_hash=config.TELEGRAM_API_HASH,
    bot_token=config.TELEGRAM_BOT_TOKEN
)

bot = TgBot(
    session_name=config.BOT_SESSION_NAME,
    tg_creds=tg_creds,
    db_prov=db,
    data_providers=[
        AlphaVantageAPI(key=config.ALPHA_VANTAGE_KEY)
    ]
)


@bot.app.on_callback_query(filter_cb_data_starts("canceled"))
async def cancellation_handler(client: PyrogramClient, query: CallbackQuery):
    await query.message.reply(
        msg_ok("Operation cancelled by user")
    )
    await query.message.delete()


@bot.app.on_callback_query(filter_cb_data_starts("confirmed --cmd delete_me"))
async def confirmed_del_tg_user(client: PyrogramClient, query: CallbackQuery):
    if bot.db.delete_user_by_tg_id(query.from_user.id) is None:
        await query.answer(
            msg_error("Failed to delete user: db error")
        )
        await query.message.delete()
        return

    await query.message.reply("👋")
    await query.message.reply(
        msg_ok(
            f"Successfully deleted ALL DATA of: {query.from_user.first_name}!"
            "\nYou can now delete this chat"
            "\nOR you could start using this bot again 👉 `/sign_in_tg` command"
        )
    )
    await query.message.delete()


@bot.app.on_message(filters.command("delete_me"))
async def cmd_del_tg_user(client: PyrogramClient, message: Message):
    found_user = bot.db.find_user_by_tg_id(message.from_user.id)
    if isinstance(found_user, Failure):
        await message.reply(
            msg_error(
                "Could not delete user: not signed in"
                "\n👉 try `/sign_in_tg`"
            )
        )
        return

    confirmation = confirmation_markup(
        f"confirmed --cmd delete_me",
        "canceled --cmd delete_me"
    )

    await message.reply(
        "Are you sure you want to delete --ALL YOUR DATA--?",
        reply_markup=confirmation,
        parse_mode=enums.ParseMode.MARKDOWN
    )


@bot.app.on_message(filters.command("settings"))
async def cmd_settings(client: PyrogramClient, message: Message):
    user_settings = bot.db.get_settings_of_user(message.from_user.id)
    if isinstance(user_settings, Failure):
        await message.reply(
            msg_error(
                "Failed to retrieve settings: user not found"
                "\n👉 try `/sign_in_tg` and then try to run `/settings` again"
            )
        )
        return

    # if settings None
    #   -> force user to set providers for each type
    #   = list all data providers with type = we need a builder for reply markup
    await message.reply(
        "Settings: wow, such *empty* 🐶"
        "\n\nYou need to configure data providers for stock market"
    )


async def get_user_providers(tg_user_id: int, provider_type=None):
    # if provider_type is None:
    #     bot.db.get_settings_of_user(tg_user_id)
    raise NotImplementedError()


async def get_available_providers():
    # get all providers passed to bot instance
    raise NotImplementedError()


@bot.app.on_message(filters.command("sign_in_tg"))
async def cmd_sign_in_tg(client: PyrogramClient, message: Message):
    tg_id = message.from_user.id
    match bot.db.find_user_by_tg_id(tg_id):
        case Success(_):
            await message.reply(
                msg_ok(
                    f"Welcome back, {message.from_user.first_name}!"
                )
            )

        case Failure(_):
            user_added = bot.db.add_user_by_tg_id(tg_id)

            if user_added is None:
                await message.reply(
                    msg_error(
                        "Failed to sign in via your telegram acc"
                        "\n👉 try `/delete_me` and then try to sign in again"
                    )
                )
                return

            await message.reply(
                msg_ok(
                    f"You successfully signed in, {message.from_user.first_name}!"
                )
            )

            await message.reply(
                msg_warning(
                    "You should choose providers of market data!"
                    "\n👉 use `/settings` command to set up providers"
                )
            )


@bot.app.on_message(filters.command("search_stock_market"))
async def cmd_search_stock_market(client: PyrogramClient, message: Message):
    query = message.text.replace("/search_stock_market", "").strip()
    if query is None or query == "" or query == " ":
        await message.reply(
            msg_warning(
                "Please provide a stock ticker"
                " or a message to search"
                " through available instruments"
            )
        )
        return

    res = bot.db.get_settings_of_user(message.from_user.id)
    match res:
        case Failure("Query is empty"):
            await message.reply(msg_error("You are not signed in"))
            return

        case Failure(wtf):
            raise RuntimeError(f"Internal bot error: {wtf}")

        case Success(settings):
            if settings is None:
                await message.reply(
                    msg_error(
                        "Settings not set"
                        "\n\nYou need to configure data"
                        " providers for stock market in settings"
                    )
                )
                return

            prov_name: str = settings["provider_stock_market"]
            prov = bot.get_prov_stock_market(prov_name)

            # retrieve available stocks, bond, currencies
            search_res: list[SearchQueryRes] | None = await prov.search_stock_market(query)

            if search_res is None or search_res == []:
                await message.reply(
                    msg_error(
                        "Failed to retrieve instrument data. "
                        "Try searching with different keywords."
                    )
                )
                return

            for x in search_res:
                await message.reply(
                    x.to_markdown(),
                    parse_mode=enums.ParseMode.MARKDOWN
                )


# run the bot
if __name__ == "__main__":
    print("Starting bot...")
    bot.run()
    print("Exiting bot...")
