from pyrogram import filters
from pyrogram.filters import Filter
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton


# Custom filters:


def filter_cb_data_is(data: str) -> Filter:
    async def func(flt, _, query: CallbackQuery):
        return flt.data == query.data

    # "data" kwarg is accessed with "flt.data" above
    return filters.create(func, data=data)


def filter_cb_data_contains(data: str) -> Filter:
    async def func(flt, _, query: CallbackQuery):
        return flt.data in query.data

    return filters.create(func, data=data)


def filter_cb_data_starts(data: str) -> Filter:
    async def func(flt, _, query: CallbackQuery):
        return query.data.startswith(flt.data)

    return filters.create(func, data=data)


def confirmation_markup(cb_data_confirmed: str, cb_data_canceled: str) -> InlineKeyboardMarkup:
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
