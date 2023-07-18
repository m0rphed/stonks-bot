from pyrogram.types import CallbackQuery
from formatting import msg_warning


async def finish_callback_query(callback_query: CallbackQuery, msg_text: str = None, delete_prev: bool = False):
    if msg_text is not None:
        await callback_query.message.reply(msg_text)

    if delete_prev:
        await callback_query.message.delete(True)

    await callback_query.answer()


async def tracking_cancellation(callback_query: CallbackQuery):
    await finish_callback_query(
        callback_query,
        msg_text=msg_warning("Tracking canceled by user."),
        delete_prev=True
    )
