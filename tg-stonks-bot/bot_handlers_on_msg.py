from functools import partial
from typing import Any

from pyrogram import Client, enums, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from returns.result import Failure, Success, Result

from app_container import AppContainer
from bot_helpers import (
    confirmation_markup,
    cancel_btn,
    _running_without_providers
)
from db.helpers import res_to_instrument, try_get_user_by_id, try_get_settings_of_user, ensure_awaited
from db.errors import DbError
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
from user_settings import UserSettings


async def cmd_delete_me(_client: Client, message: Message, app: AppContainer):
    found_user: Result[dict, Any] = try_get_user_by_id(
        app.database,
        message.from_user.id
    )

    # if no user was found - reply with error message;
    # -then exit right away
    if isinstance(found_user, Failure):
        await message.reply(
            msg_error(
                "Could not delete user: user not found"
                "\n👉 try `/sign_in_tg`"
            )
        )
        return

    # if user exist - we should prepare confirmation markup
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
    found_settings: Result[UserSettings, Any] = try_get_settings_of_user(
        app.database,
        message.from_user.id
    )
    # TODO: by default we notify the user
    #  that if there something wrong - it probably because
    #   user was not found, but it actually could be internal error
    #   which we do not handle -> handle these types of errors
    if isinstance(found_settings, Failure):
        await message.reply(
            msg_error(
                "Failed to retrieve settings: user not found"
                "\n👉 try `/sign_in_tg` and then try to run `/settings` again"
            )
        )
        return

    settings: UserSettings = found_settings.unwrap()
    # TODO: maybe we need to list all data providers with type -> use reply markup builder
    if settings.is_all_providers_null() is None:
        await message.reply(
            "Settings: wow, such *empty* 🐶"
            "\n\nConsider configuring data providers"
            " for stock market, currency exchanges etc."
        )
        return

    await message.reply(settings.to_markdown())


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
    _id = message.from_user.id

    match try_get_user_by_id(app.database, _id):
        case Success(_):
            await message.reply(
                msg_ok(
                    f"Welcome back, {message.from_user.first_name}!"
                )
            )

        case Failure(_err):
            user_added = app.database.add_new_user(_id)

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
                    "You should choose providers of stock market & currencies rates data!"
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

    res: Result[UserSettings, Any] = try_get_settings_of_user(app.database, message.from_user.id)
    match res:
        case Failure(err) if isinstance(err, DbError) and str(err) == "Query is empty":
            await message.reply(
                msg_error(
                    "You are not authenticated:\n"
                    "➜ Could not retrieve providers settings"
                )
            )
            return

        case Failure(unexpected_err):
            # TODO: implement more case for different errors
            raise RuntimeError(f"Internal bot error: {unexpected_err}")

        case Success(settings) if isinstance(settings, UserSettings):
            if settings.is_all_providers_null() or settings.provider_stock_market is None:
                await message.reply(
                    msg_error(
                        "Needed provider is not set"
                        "\n\nYou need to set --stock market "
                        "data provider-- in settings"
                    ),
                    parse_mode=enums.ParseMode.MARKDOWN
                )
                return

            # TODO: handle case when specified provider
            #  is not available or provider name was simply set incorrectly
            sm_prov = app.stock_market_provider_by_name(
                settings.provider_stock_market.name
            )

            # retrieve available stocks, bond, currencies
            search_res: list[SearchQueryRes] | None = ensure_awaited(
                sm_prov.search_stock_market,
                search_query
            )

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
                "\n • ticker: `AAPL`, etc "
                "\n • price: `231`, `159.5`, etc (value in currency of exchange)"
                "\n\nExample of full command: `/track_by_ticker SBER.ME 138.5`"
            )
        )
        return

    ticker, price = args
    # TODO: rewrite to result returning functions
    res: Result[UserSettings, Any] = try_get_settings_of_user(
        app.database,
        message.from_user.id
    )

    match res:
        case Failure(err) if isinstance(err, DbError) and str(err) == "Query is empty":
            await message.reply(
                msg_error(
                    "Error: user not found"
                    "\n\n👉 try `/sign_in_tg`"
                )
            )

        case Failure(unexpected_error):
            await message.reply(
                msg_error(
                    "Error: unexpected error"
                    f" occurred:\n{unexpected_error}"
                )
            )

        case Success(settings) if isinstance(settings, UserSettings):
            if settings.is_all_providers_null() and settings.provider_stock_market is None:
                await message.reply(
                    msg_error(
                        "Error: provider for --stock market data-- was not set"
                        "\n\n👉 try `/settings` or `/set_providers`"
                    ),
                    parse_mode=enums.ParseMode.MARKDOWN
                )
                return

            # TODO: handle case when specified provider
            #  is not available or provider name was simply set incorrectly
            sm_prov = app.stock_market_provider_by_name(
                settings.provider_stock_market.name
            )

            security = ensure_awaited(sm_prov.get_security_by_ticker, ticker)
            # TODO: rewrite to result-returning functions
            instr_res = app.database.find_stock_market_instrument(
                security.symbol,
                security.data_provider
            )

            if isinstance(instr_res, Success):
                tracking_obj = create_tracking_obj(
                    user=settings.unwrap(),
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
                    user=settings.unwrap(),
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
