from pyrogram import filters
from pyrogram.filters import Filter
from pyrogram.types import CallbackQuery


def callback_data_is(data: str) -> Filter:
    async def func(flt, _, query: CallbackQuery):
        return flt.data == query.data

    # "data" kwarg is accessed with "flt.data" above
    return filters.create(func, data=data)


def callback_data_contains(data: str) -> Filter:
    async def func(flt, _, query: CallbackQuery):
        return flt.data in query.data

    return filters.create(func, data=data)


def callback_data_starts(data: str) -> Filter:
    async def func(flt, _, query: CallbackQuery):
        return query.data.startswith(flt.data)

    return filters.create(func, data=data)
