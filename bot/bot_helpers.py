import secrets
from formatting import msg_warning
from pyrogram.types import Message
from models import BotUserEntity
from supabase_funcs import check_user


DEFAULT_KEY_LEN = 10


def get_random_key(key_length: int = DEFAULT_KEY_LEN) -> str:
    key = secrets.token_hex(key_length)[:key_length]
    return key


async def authenticated_users_only(msg_to_reply: Message) -> BotUserEntity | None:
    user = check_user(msg_to_reply.from_user.id)
    if user is None:
        await msg_to_reply.reply(
            msg_warning("You are NOT authenticated to do this.")
        )
        return None

    return user
