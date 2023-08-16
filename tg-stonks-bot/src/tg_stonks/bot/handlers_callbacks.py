from functools import partial

from pyrogram import Client
from pyrogram.handlers import CallbackQueryHandler
from pyrogram.types import CallbackQuery

import tg_stonks.bot.custom_filters as flt
from tg_stonks.bot.app_container import AppContainer
from tg_stonks.bot.helpers import chose_provider_markup
from tg_stonks.bot.formatting import msg_error, msg_ok


async def provider_set_handler(_client: Client, query: CallbackQuery, app: AppContainer):
    params = query.data.replace("confirmed --cmd prov", "").strip()
    prov_t, prov_name = params.split()
    prov_settings = _providers_settings(prov_t, prov_name)

    app.database.update_user(query.from_user.id, {
        "settings": prov_settings
    })

    await query.message.reply(msg_ok("User settings updated!"))
    await query.message.delete()


async def set_providers_handler(_client: Client, query: CallbackQuery, app: AppContainer):
    prov_name = query.data.replace("confirmed --cmd prvs", "").strip()

    for prov in app.data_providers:
        if prov.provider_name == prov_name:
            msg, markup = chose_provider_markup(prov)
            await query.message.reply(
                msg,
                reply_markup=markup
            )
            await query.message.delete()
            return


async def cancellation_cb_handler(_client: Client, query: CallbackQuery, app: AppContainer):
    await query.message.reply(
        msg_ok("Operation cancelled by user")
    )
    await query.message.delete()


async def confirmed_delete_me(_client: Client, query: CallbackQuery, app: AppContainer):
    if app.database.delete_user_by_tg_id(query.from_user.id) is None:
        await query.answer(
            msg_error("Failed to delete user: database error")
        )
        await query.message.delete()
        return

    await query.message.reply("👋")
    await query.message.reply(
        msg_ok(
            f"Successfully deleted ALL DATA of: {query.from_user.first_name}!"
            "\nYou can now delete this chat"
            "\nOR you could start using this tg-stonks-bot again 👉 `/sign_in_tg` command"
        )
    )
    await query.message.delete()


def get_callbacks_handlers(x: AppContainer) -> list[CallbackQueryHandler]:
    return [
        CallbackQueryHandler(
            partial(provider_set_handler, app=x),
            flt.callback_data_starts("confirmed --cmd prov")
        ),
        CallbackQueryHandler(
            partial(set_providers_handler, app=x),
            flt.callback_data_starts("confirmed --cmd prvs")
        ),
        CallbackQueryHandler(
            partial(cancellation_cb_handler, app=x),
            flt.callback_data_starts("canceled")
        ),
        CallbackQueryHandler(
            partial(confirmed_delete_me, app=x),
            flt.callback_data_starts("confirmed --cmd delete_me")
        ),
    ]
