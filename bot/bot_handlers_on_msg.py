from functools import partial

from pyrogram import Client, enums, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from returns.result import Failure, Success

from app_container import AppContainer
from bot_helpers import (
    confirmation_markup,
    cancel_btn,
    _running_without_providers
)
from db_helpers import res_to_instrument
from formatting import (
    msg_error,
    msg_warning,
    msg_ok,
    msg_list_providers
)
from models import (
    SearchQueryRes,
    create_tracking_obj,
    InstrumentType,
    InstrumentEntity
)


async def cmd_delete_me(_client: Client, message: Message, app: AppContainer):
    found_user = app.database.find_user_by_tg_id(message.from_user.id)
    if isinstance(found_user, Failure):
        await message.reply(
            msg_error(
                "Could not delete user: not signed in"
                "\n👉 try `/sign_in_tg`"
            )
        )
        return

    confirmation = confirmation_markup(
        "confirmed --cmd delete_me",
        "canceled --cmd delete_me"
    )

    await message.reply(
        "Are you sure you want to delete --ALL YOUR DATA--?",
        reply_markup=confirmation,
        parse_mode=enums.ParseMode.MARKDOWN
    )


async def cmd_settings(_client: Client, message: Message, app: AppContainer):
    user_settings = app.database.get_settings_of_user(message.from_user.id)
    if isinstance(user_settings, Failure):
        await message.reply(
            msg_error(
                "Failed to retrieve settings: user not found"
                "\n👉 try `/sign_in_tg` and then try to run `/settings` again"
            )
        )
        return

    # TODO: if settings None
    #   -> force user to set providers for each type
    #   = list all data providers with type = we need a builder for reply markup
    if user_settings.unwrap() is None:
        await message.reply(
            "Settings: wow, such *empty* 🐶"
            "\n\nYou need to configure data providers for stock market"
        )
        return

    await message.reply(f"Setting is {user_settings.unwrap()}")


async def cmd_set_providers(_client: Client, message: Message, app: AppContainer):
    if len(app.data_providers) == 0:
        await _running_without_providers(message)
        return

    buttons = []
    for data_prov in app.data_providers:
        name = data_prov.provider_name
        btn = InlineKeyboardButton(
            f"🔧 Set up '{name}'",
            callback_data=f"confirmed --cmd prvs {name}"
        )
        buttons.append([btn])

    # add cancellation button
    buttons.append(
        [cancel_btn("--cmd prvs")]
    )

    await message.reply(
        msg_list_providers(app.data_providers),  # message contains all available providers
        reply_markup=InlineKeyboardMarkup(buttons)  # reply markup with all available providers
    )


async def cmd_providers(_client: Client, message: Message, app: AppContainer):
    if len(app.data_providers) == 0:
        await _running_without_providers(message)
        return

    await message.reply(
        msg_list_providers(
            app.data_providers
        )
    )


async def cmd_sign_in_tg(_client: Client, message: Message, app: AppContainer):
    tg_id = message.from_user.id
    match app.database.find_user_by_tg_id(tg_id):
        case Success(_):
            await message.reply(
                msg_ok(
                    f"Welcome back, {message.from_user.first_name}!"
                )
            )

        case Failure(_):
            user_added = app.database.add_user_by_tg_id(tg_id)

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


async def cmd_search_stock_market(_client: Client, message: Message, app: AppContainer):
    search_query = message.text.replace("/search_stock_market", "").strip()
    if search_query is None or search_query == "" or search_query == " ":
        await message.reply(
            msg_warning(
                "Please provide a stock ticker"
                " or a message to search"
                " through available instruments"
            )
        )
        return

    res = app.database.get_settings_of_user(message.from_user.id)
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
            prov = app.get_prov_stock_market(prov_name)

            # retrieve available stocks, bond, currencies
            search_res: list[SearchQueryRes] | None = await prov.search_stock_market(search_query)

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


async def cmd_track_stock(_client: Client, message: Message, app: AppContainer):
    args_str = message.text.replace("/track_stock", "").strip()
    args = args_str.split()
    if len(args) != 2:
        await message.reply(
            msg_error(
                "`track_stock`: incorrect arguments"
                "\nProvide exactly two arguments separated by space:"
                "\n - ticker: `AAPL`, etc "
                "\n - price: `231`, `159.5`, etc (value in currency of exchange)"
                "\nExample of full command: `/track_by_ticker SBER.ME 138.5`"
            )
        )
        return

    ticker, price = args

    user_id: int = message.from_user.id
    user_res = app.database.find_user_by_tg_id(user_id)
    if isinstance(user_res, Failure) or user_res is None:
        await message.reply(
            msg_error(
                "Error: user not found"
                "\n\n👉 try `/sign_in_tg`"
            )
        )
        return

    user_settings: dict = user_res.unwrap().settings
    if user_settings is None:
        await message.reply(
            msg_error(
                "Error: user's settings not defined"
                "\n\n👉 try `/set_providers`"
            )
        )
        return

    if "provider_stock_market" not in user_settings.keys():
        await message.reply(
            msg_error(
                "Error: stock market data provider not set"
                "\n\n👉 try `/settings` or `/set_providers`"
            )
        )
        return

    prov_name = user_settings["provider_stock_market"]
    prov = app.get_prov_stock_market(prov_name)
    security = await prov.get_security_by_ticker(ticker=ticker)

    instr_res = app.database.find_stock_market_instrument(
        security.symbol,
        security.data_provider
    )

    if isinstance(instr_res, Success):
        tracking_obj = create_tracking_obj(
            user=user_res.unwrap(),
            instrument=instr_res.unwrap(),
            on_price=price,
        )
        _ = app.database.add_tracking(tracking_obj)
        await message.reply(msg_ok("Added for tracking"))
        return

    else:
        instr: InstrumentEntity = res_to_instrument(Success(app.database.add_instrument(
            {
                "symbol": ticker,
                "price": security.price,
                "data_provider_code": security.data_provider,
                "type": InstrumentType.sm_instrument.value
            }
        ))).unwrap()

        tracking_obj = create_tracking_obj(
            user=user_res.unwrap(),
            instrument=instr,
            on_price=price,
        )
        _ = app.database.add_tracking(tracking_obj)
        await message.reply(msg_ok("Added for tracking"))
        return


def get_commands(x: AppContainer) -> list[MessageHandler]:
    return [
        MessageHandler(partial(cmd_delete_me,           app=x), filters.command("delete_me")),
        MessageHandler(partial(cmd_settings,            app=x), filters.command("settings")),
        MessageHandler(partial(cmd_set_providers,       app=x), filters.command("set_providers")),
        MessageHandler(partial(cmd_providers,           app=x), filters.command("providers")),
        MessageHandler(partial(cmd_sign_in_tg,          app=x), filters.command("sign_in_tg")),
        MessageHandler(partial(cmd_search_stock_market, app=x), filters.command("search_stock_market")),
        MessageHandler(partial(cmd_track_stock,         app=x), filters.command("track_stock"))
    ]
