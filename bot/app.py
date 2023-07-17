from pyrogram import filters, Client as PyrogramClient
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from pyrogram import enums as pyro_enums

import creds

from models import CurrencyPairInfo, InstrumentSearchInfo
from api_alpha_vantage import get_curr_pair_info, get_stock_info, get_search_results, instrument_to_markdown
from db_funcs import get_supabase_client

BOT_NAME = "stonks-bot"

# ensure needed environment variables are loaded
creds.load_env_file("./secret/.env")

# set telegram client credentials
app = PyrogramClient(
    BOT_NAME,
    api_id=creds.get_from_env("TELEGRAM_API_API_ID"),
    api_hash=creds.get_from_env("TELEGRAM_API_API_HASH"),
    bot_token=creds.get_from_env("TELEGRAM_BOT_TOKEN")
)

supabase = get_supabase_client()


@app.on_message(filters.command("auth"))
async def authenticate_user(client: PyrogramClient, message: Message):
    """Handler for "/auth" command
    """

    # telegram's user id is supposed to be unique (not affected by username change etc.)
    user_id = message.from_user.id

    # check if the user is already authenticated
    user = supabase.table("bot_users").select("*").eq(
        "tg_user_id", user_id).execute()

    if len(user.data) > 0:
        await message.reply("⚠️ You are already authenticated.")
        return

    # save user's unique id to DB
    supabase.table("bot_users").insert({"tg_user_id": user_id}).execute()
    await message.reply("✅ Authentication successful!")


@app.on_message(filters.command("track_stock"))
async def track_stock(client: PyrogramClient, message: Message):
    """Handler for "/track_stock <stock_ticker> <price_to_be_reached>" command
    """

    args = message.text.split()[1:]
    if len(args) != 2:
        await message.reply("Please provide a stock ticker and price to be reached.")
        return

    stock_ticker, price_str = args

    try:
        # exception would be raised if string could not be converted to valid float value
        price_to_be_reached = float(price_str)
    except ValueError:
        await message.reply(f"⛔ Price you provided: '{price_str}'\n- Please provide a valid price value e.g. 👉 142, 255.5, 0.034")
        return

    # retrieve stock info using get_stock_info
    stock_info = await get_stock_info(stock_ticker)

    if stock_info is None:
        await message.reply(
            "⛔ Failed to retrieve stock data. Try searching stocks with command '/search_stock <ticker>'.")
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
            "Confirm", callback_data=f"tracking_confirmed_{stock_ticker}-{price_to_be_reached}"
        )]]
    )

    await message.reply_text(
        reply_message,
        reply_markup=keyboard,
        parse_mode=pyro_enums.ParseMode.MARKDOWN
    )


@app.on_message(filters.command("track_currency"))
async def track_currency(client: PyrogramClient, message: Message):
    """Handler for "/track_currency <from currency symbol> <to currency symbol>" command
    Example:
        /track USD EUR
        /track BTC USD
    """

    args = message.text.split()[1:]
    if len(args) != 2:
        await message.reply("Please provide a stock ticker and price to be reached.")
        return

    from_curr, to_curr = args

    # retrieve currency pair exchange rate
    curr: CurrencyPairInfo | None = await get_curr_pair_info(from_curr, to_curr)

    if curr is None:
        await message.reply(
            f"⛔ Failed to retrieve currency pair → from '{from_curr}' to '{to_curr}'."
            + "Try providing different currency symbol e.g. 👉 \n\t/track_currency USD CNY\n\t/track_currency BTC USD"
        )
        return

    # create reply message with stock info and a button to confirm tracking
    reply_message = f"**{curr.name_from}** 👉 **{curr.name_to}**" \
                    f"`{curr.code_from}` 👉 `{curr.code_to}`" \
                    f"• Current rate: {curr.rate}\n" \
                    f"• Last refreshed: {curr.last_datetime.strftime('%Y.%m.%d %H:%M')}\n\n" \
                    f"If this is the correct currency pair you want to track, click the button below to confirm."

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(
            "Confirm", callback_data=f"tracking_currency_confirmed>{curr.code_from}-{curr.code_to}"
        )]]
    )

    await message.reply_text(
        reply_message,
        reply_markup=keyboard,
        parse_mode=pyro_enums.ParseMode.MARKDOWN
    )


@app.on_message(filters.command("search_stock"))
async def search_stock(client: PyrogramClient, message: Message):
    """Handler for "/search_stock <search query>" command
    """

    query = message.text.replace("/search_stock", "").strip()
    if query is None or query == "" or query == " ":
        await message.reply("Please provide a stock ticker or a message to search through available instruments")
        return

    # retrieve available stocks, bond, currencies
    xs: list[InstrumentSearchInfo] | None = await get_search_results(query)

    if xs is None or xs == []:
        await message.reply(
            "Failed to retrieve instrument data. Try searching with different keywords.")
        return

    for inst in xs:
        await message.reply(instrument_to_markdown(inst), parse_mode=pyro_enums.ParseMode.MARKDOWN)


@app.on_callback_query()
async def handle_button_click(client: PyrogramClient, callback_query: CallbackQuery):
    """Handler for button callbacks
    """

    user_id = callback_query.from_user.id
    data = callback_query.data

    if data.startswith("tracking_currency_confirmed>"):
        curr_codes: list = data.replace(
            "tracking_currency_confirmed>", "").split("-")
        curr_info: CurrencyPairInfo | None = await get_curr_pair_info(curr_codes[0], curr_codes[1])

        # TODO: remove unnecessary api request before adding to db in callback
        if curr_info is None:
            await callback_query.answer("⛔ Failed to retrieve stock data.")
            return

        try:
            # TODO: check if currency pair is in INSTRUMENTS
            db_curr_pair = supabase.table("instruments").select("*"
                                                                ).eq("is_curr_pair", True
                                                                     ).eq("data_provider", "alpha_vantage"
                                                                          ).eq("code_curr", f"{curr_info.code_from}-{curr_info.code_to}"
                                                                               ).execute()

            if len(db_curr_pair.data) == 1:
                row = db_curr_pair.data[0]
                raise NotImplementedError(
                    "That means that this currency pair is tracked by at least 1 user"
                    "-> We need to get its `table('instruments').id`"
                    "-> We need to get our `table('bot_users').id` which == table('bot_users').select('*').eq('tg_user_id', user_id)"
                    "-> We need to define how frequent we want to receive messages = 'daily', 'on_change', ...")

            if len(db_curr_pair.data) == 0:
                raise NotImplementedError(
                    "No such currency pair tracked by anyone -> you need to upd INSTRUMENTS")

            if len(db_curr_pair.data) > 1:
                raise NotImplementedError("Impossible case, table corrupted")

            # save tracking details to Supabase linked to user's telegram account
            supabase.table("tracking").insert({
                "user_id": user_id,
                "ticker": stock_ticker,
                "on_price_value": on_price_value
            }).execute()

        except Exception as e:  # TODO: handle try adding already tracking stock
            await callback_query.answer(f"⛔ Tracking failed: {e}")
            return

    if data.startswith("tracking_confirmed_"):
        prefix, on_price_value = data.split("-")
        stock_ticker = prefix.replace("tracking_confirmed_", "")

        # TODO: remove unnecessary api request before adding to db in callback
        stock_info = await get_stock_info(stock_ticker)

        if stock_info is None:
            await callback_query.answer("⛔ Failed to retrieve stock data.")
            return

        try:
            # save tracking details to Supabase linked to user's telegram account
            supabase.table("tracking").insert({
                "user_id": user_id,
                "ticker": stock_ticker,
                "on_price_value": on_price_value
            }).execute()

        except Exception as e:  # TODO: handle try adding already tracking stock
            await callback_query.answer(f"⛔ Tracking failed: {e}")
            return

        await callback_query.answer("✅ Tracking started successfully.")


# run the bot
if __name__ == "__main__":
    import asyncio
    print("Starting bot...")
    asyncio.run(app.run())
    print("Exiting bot...")
