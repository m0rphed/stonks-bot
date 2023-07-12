from pyrogram import filters, Client as PyrogramClient
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.errors import UserNotParticipant
from creds import get_from_toml
from supabase import create_client, Client as DbClient


BOT_NAME = "stonks-bot"

# set telegram client credentials
tg_keys = get_from_toml("telegram-api")
bot_token = get_from_toml("telegram-bot")["token"]

app = PyrogramClient(
    BOT_NAME,
    api_id=tg_keys["api_id"],
    api_hash=tg_keys["api_hash"],
    bot_token=bot_token
)

# set bot users DB (using: https://supabase.com/)
sb_keys = get_from_toml("supabase")
supabase_url: str = sb_keys["url"]
supabase_key: str = sb_keys("key")
supabase: DbClient = create_client(supabase_url, supabase_key)


@app.on_message(filters.command("auth"))
def authenticate_user(client: PyrogramClient, message: Message):
    """Handler for "/auth" command
    """

    # Telegram's User ID is supposed to be unique (not affected by username change etc.)
    user_id = message.from_user.id

    # Check if the user is already authenticated
    user = supabase.table("users").select().eq(
        "user_id", user_id).limit(1).execute()

    if len(user["data"]) > 0:
        message.reply("You are already authenticated.")
        return

    # Check if the user is a member of a specific channel
    channel_username = "YOUR_CHANNEL_USERNAME"
    try:
        app.get_chat_member(chat_id=channel_username, user_id=user_id)
    except UserNotParticipant:
        message.reply("Please join the required channel to authenticate.")
        return

    # Save user's unique id to Supabase
    supabase.table("users").insert({"user_id": user_id}).execute()
    message.reply("Authentication successful.")


@app.on_message(filters.command("track"))
def track_stock(client: PyrogramClient, message: Message):
    """Handler for "/track <stock_ticket> <price_to_be_reached>" command
    """

    user_id = message.from_user.id
    args = message.text.split(" ")[1:]
    if len(args) != 2:
        message.reply("Please provide a stock ticket and price to be reached.")
        return

    stock_ticket, price_to_be_reached = args

    # Save tracking details to Supabase linked to user's telegram account
    supabase.table("tracking").insert({
        "user_id": user_id,
        "stock_ticket": stock_ticket,
        "price_to_be_reached": price_to_be_reached
    }).execute()

    message.reply("Stock tracking started successfully.")

@app.on_message(filters.command("start"))
def start_command(client, message):
    # Generate a unique deep link for the user
    deep_link = app.export_session_string()

    # Create an inline keyboard with a button that opens the bot with the deep link
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(
            "Authenticate", url=f"t.me/my_bot?start={deep_link}")]]
    )

    # Send the user a message with the inline keyboard
    message.reply_text(
        "Click the button below to authenticate:", reply_markup=keyboard)


# Run the bot
if __name__ == "__name__":
    app.run()
