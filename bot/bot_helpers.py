import secrets
from formatting import msg_error, msg_warning
from pyrogram.types import Message
from models import BotUserEntity
from supabase_funcs import check_user


DEFAULT_KEY_LEN = 10


def get_random_key(key_length: int = DEFAULT_KEY_LEN) -> str:
    key = secrets.token_hex(key_length)[:key_length]
    return key


async def authenticated_users_only(msg: Message) -> BotUserEntity | None:
    user = check_user(msg.from_user.id)
    if user is None:
        await msg.reply(
            msg_warning("You are NOT authenticated to do this.")
        )
        return None

    return user


async def check_argument_count(msg: Message, count: int) -> None:
    args = msg.text.split()[1:]
    if len(args) != count:
        await msg.reply(
            msg_error(
                "Please provide a stock ticker and price to be reached.")
        )
        return
