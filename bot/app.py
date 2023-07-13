from pyrogram import filters, Client as PyrogramClient
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from pyrogram.errors import UserNotParticipant
from creds import load_dotenv, get_from_env
from supabase import create_client, Client as DbClient
from stocks_alpha_vantage import get_stock_info

BOT_NAME = "stonks-bot"

# ensure needed environment variables are loaded
load_dotenv("./secret/.env")

# set telegram client credentials
app = PyrogramClient(
    BOT_NAME,
    api_id=get_from_env("TELEGRAM_API_API_ID"),
    api_hash=get_from_env("TELEGRAM_API_API_HASH"),
    bot_token=get_from_env("TELEGRAM_BOT_TOKEN")
)

# set bot users DB (using: https://supabase.com/)
supabase_url: str = get_from_env("SUPABASE_URL")
# TODO: use public supabase key if possible (now using service_role)
supabase_key: str = get_from_env("SUPABASE_SEC_KEY")
supabase: DbClient = create_client(supabase_url, supabase_key)


@app.on_message(filters.command("auth"))
def authenticate_user(client: PyrogramClient, message: Message):
    """Handler for "/auth" command
    """

    # telegram's user id is supposed to be unique (not affected by username change etc.)
    user_id = message.from_user.id

    # check if the user is already authenticated
    user = supabase.table("users").select("*").eq(
        "user_id", user_id).execute()

    if len(user.data) > 0:
        message.reply("You are already authenticated.")
        return

    # TODO: why do we even need to check THAT???
    # # check if the user is a member of a specific channel
    # channel_username = "YOUR_CHANNEL_USERNAME"
    # try:
    #     app.get_chat_member(chat_id=channel_username, user_id=user_id)
    # except UserNotParticipant:
    #     message.reply("Please join the required channel to authenticate.")
    #     return

    # save user's unique id to DB
    supabase.table("users").insert({"user_id": user_id}).execute()
    message.reply("Authentication successful.")


@app.on_message(filters.command("track"))
def track_stock(client: PyrogramClient, message: Message):
    """Handler for "/track <stock_ticker> <price_to_be_reached>" command
    """

    args = message.text.split(" ")[1:]
    if len(args) != 2:
        message.reply("Please provide a stock ticker and price to be reached.")
        return

    stock_ticker, price_to_be_reached = args

    # retrieve stock info using get_stock_info
    stock_info = get_stock_info(stock_ticker)

    if stock_info is None:
        message.reply(
            "Failed to retrieve stock data. Try searching stocks with command '/search <ticker>'.")
        return

    # create reply message with stock info and a button to confirm tracking
    reply_message = f"Stock information:\n\n" \
                    f"Ticket: {stock_info.ticker}\n" \
                    f"Price: {stock_info.price}\n" \
                    f"Exchange: {stock_info.exchange}\n" \
                    f"Stock Real Name: {stock_info.stock_real_name}\n" \
                    f"Percentage Delta: {stock_info.per_day_price_delta_percentage}%\n\n" \
                    f"If this is the correct stock you want to track, click the button below to confirm."

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(
            "Confirm Tracking", callback_data=f"confirm_track_{stock_ticker}-{price_to_be_reached}")]]
    )

    message.reply_text(reply_message, reply_markup=keyboard)


@app.on_callback_query()
def handle_button_click(client: PyrogramClient, callback_query: CallbackQuery):
    """Handler for button callbacks
    """

    user_id = callback_query.from_user.id
    data = callback_query.data
    if data.startswith("confirm_track_"):
        prefix, on_price_value = data.split("-")
        stock_ticker = prefix.replace("confirm_track_", "")

        # retrieve stock info using get_stock_info
        stock_info = get_stock_info(stock_ticker)

        if stock_info is None:
            callback_query.answer("Failed to retrieve stock data.")
            return

        # save tracking details to Supabase linked to user's telegram account
        supabase.table("tracking").insert({
            "user_id": user_id,
            "ticker": stock_ticker,
            "on_price_value": on_price_value
        }).execute()

        callback_query.answer("Stock tracking started successfully.")


# run the bot
if __name__ == "__main__":
    print("Starting bot...")
    app.run()
    print("STONKS!")
