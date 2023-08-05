from pyrogram import filters
from pyrogram.filters import Filter
from pyrogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton

from db import IDatabase
from formatting import msg_error


# Custom filters:


def flt_callback_data_is(data: str) -> Filter:
    async def func(flt, _, query: CallbackQuery):
        return flt.data == query.data

    # "data" kwarg is accessed with "flt.data" above
    return filters.create(func, data=data)


def flt_callback_data_contains(data: str) -> Filter:
    async def func(flt, _, query: CallbackQuery):
        return flt.data in query.data

    return filters.create(func, data=data)


def flt_callback_data_starts(data: str) -> Filter:
    async def func(flt, _, query: CallbackQuery):
        return query.data.startswith(flt.data)

    return filters.create(func, data=data)


async def ensure_user_authenticated(db: IDatabase, msg_to_reply: Message):
    found_user = db.check_user(msg_to_reply.from_user.id)
    if found_user is None:
        await msg_to_reply.reply(msg_error("User not authenticated"))
        return

    return found_user


def reply_markup_confirmation(cb_data_confirmed: str, cb_data_canceled: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[
            InlineKeyboardButton(
                "Confirm", callback_data=cb_data_confirmed
            ),
            InlineKeyboardButton(
                "Cancel", callback_data=cb_data_canceled
            )
        ]]
    )
