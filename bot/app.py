from pyrogram import filters, Client as PyrogramClient
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from pyrogram import enums

import creds
import json

from models import BotUserEntity, CurrencyPairInfo, InstrumentEntity, InstrumentSearchInfo, StockInfo
from api_alpha_vantage import get_curr_pair_info, get_stock_info, get_search_results, instrument_to_markdown
from db_funcs import get_supabase_client
from supabase_funcs import add_instrument, add_user_by_id, check_instrument_by_ticker, check_user, add_tracking

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


def msg_warning(msg: str):
    return "⚠️ " + msg


def msg_error(msg: str):
    return "⛔ " + msg


def msg_ok(msg: str):
    return "✅ " + msg


async def authenticated_users_only(tg_user_id: int, chat_id: int) -> BotUserEntity | None:
    user = check_user(tg_user_id)
    if user is None:
        await app.send_message(
            chat_id,
            msg_warning("You are NOT authenticated to do this.")
        )
        return None

    return user


@app.on_message(filters.command("auth"))
async def auth_user(client: PyrogramClient, message: Message):
    """User authentication command
    """

    # user_id is unique & not affected by username change etc.
    user_id = message.from_user.id

    # check if the user is already authenticated
    user = check_user(user_id)
    if user is not None:
        await message.reply(msg_warning("You are already authenticated."))
        return

    user_added = add_user_by_id(user_id)

    if user_added is not None:
        await message.reply(msg_ok("Authentication successful!"))
        return

    await message.reply(
        msg_error("Authentication failed for your telegram account;\n"
                  "try `/erase_me` - then try again."),
        parse_mode=enums.ParseMode.MARKDOWN
    )


@app.on_message(filters.command("portfolio"))
async def show_portfolio(client: PyrogramClient, message: Message):
    """shows portfolio of the user: tracked equities, currency pairs, crypto pairs 
    """
    raise NotImplementedError("ups, not done this part yet :D")


@app.on_message(filters.command("track_stock"))
async def track_stock(client: PyrogramClient, message: Message):
    """adds new tracking of a stock: "/track_stock <stock_ticker> <price>"
    """
    user_db_obj: BotUserEntity | None = await authenticated_users_only(
        tg_user_id=message.from_user.id,
        chat_id=message.chat.id
    )

    if user_db_obj is None:
        return

    args = message.text.split()[1:]
    if len(args) != 2:
        await message.reply(
            msg_error(
                "Please provide a stock ticker and price to be reached.")
        )
        return

    ticker, price_str = args
    try:
        # exception would be raised
        # if string could not be converted to valid float value
        price_to_be_reached = float(price_str)
    except ValueError:
        await message.reply(
            msg_error(
                f"Price you provided: '{price_str}'\n"
                "- Please provide a valid price value"
                " e.g. 👉 142, 255.5, 0.034")
        )
        return

    # if all correct - we prepare to track new instrument:
    #   by retrieving it from "instruments" table, and then adding it to "tracking" table,
    #   or by requesting it from preferred API - then adding both to "instruments" and to "tracking" tables
    new_stock: None | dict = None
    tracking: None | dict = None
    reply_message: None | str = None

    # check if stock ticker is tracked by anyone
    # (which means that its ticker exist in the "instruments" table)
    stock_db_obj: InstrumentEntity | None = check_instrument_by_ticker(ticker, "alpha_vantage")
    if stock_db_obj is not None:
        tracking = {
            "tracked_instrument": stock_db_obj.id,
            "tracked_by_user": user_db_obj.id,
            "notify": "on_change",
            "on_price": float(price_to_be_reached)
        }

        # create reply message with stock info from db
        reply_message = f"Stock information:\n\n" \
                        f"Ticket: {stock_db_obj.ticker}\n" \
                        f"Price: {stock_db_obj.price}\n" \
                        f"Exchange: {stock_db_obj.code_exchange}\n" \
                        f"👉 provided by: `alpha_vantage`\n" \
                        f"\nIf this is the correct stock you want to track, click the button below to confirm."

    # if not found in "instruments" -> try retrieve from API
    else:
        # retrieve stock info using get_stock_info
        stock_api: StockInfo | None = await get_stock_info(ticker)
        if stock_api is None:
            await message.reply(
                msg_error(
                    f"Failed to retrieve stock data by provided symbol: {ticker}.\n"
                    "Try searching stocks with command '/search_stock <ticker>' first.")
            )
            return

        # prepare fields of new instrument that to be inserted to the table
        new_stock: dict = {
            "is_curr_pair": False,
            "is_crypto_pair": False,
            "data_provider": "alpha_vantage",
            "price": stock_api.price,
            "code_exchange": stock_api.exchange,
            "ticker": stock_api.symbol
        }

        tracking = {
            # link to the new instrument we've just inserted
            "tracked_instrument": "",
            "tracked_by_user": user_db_obj.id,
            "notify": "on_change",
            "on_price": float(price_to_be_reached)
        }

        # create reply message with stock info from API
        reply_message = f"Stock information:\n\n" \
                        f"Ticket: {stock_api.symbol}\n" \
                        f"Price: {stock_api.price}\n" \
                        f"Exchange: {stock_api.exchange}\n" \
                        f"Change: {stock_api.change}\n" \
                        f"Percentage change: {stock_api.change_percent}\n" \
                        f"👉 provided by: `alpha_vantage`\n" \
                        f"\nIf this is the correct stock you want to track, click the button below to confirm."

    # prepare data to pass to the callback
    data = {
        "new_instrument": "" if new_stock is None else new_stock,
        "tracking": tracking
    }

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(
            "Confirm", callback_data=f"tracking_stock_confirmed>{ticker}-{price_to_be_reached}>{json.dumps(data)}"
        )], [InlineKeyboardButton(
            "❌ Cancel", callback_data=f"tracking_stocked_canceled"
        )]]
    )

    await message.reply_text(
        reply_message,
        reply_markup=keyboard,
        parse_mode=enums.ParseMode.MARKDOWN
    )


@app.on_message(filters.command("track_currency"))
async def track_currency(client: PyrogramClient, message: Message):
    """Handler for "/track_currency <from currency symbol> <to currency symbol>" command
    Example:
        /track USD EUR
        /track BTC USD
    """
    raise NotImplementedError(
        "have not rewritten to work with new sb functions patch")
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
        parse_mode=enums.ParseMode.MARKDOWN
    )


@app.on_message(filters.command("search_stock"))
async def search_stock(client: PyrogramClient, message: Message):
    """searches for stock or any equity covered by the API
    - example: "/search_stock <search query>" command
    """

    query = message.text.replace("/search_stock", "").strip()
    if query is None or query == "" or query == " ":
        await message.reply(msg_warning("Please provide a stock ticker or a message to search through available instruments"))
        return

    # retrieve available stocks, bond, currencies
    xs: list[InstrumentSearchInfo] | None = await get_search_results(query)

    if xs is None or xs == []:
        await message.reply(msg_error("Failed to retrieve instrument data. Try searching with different keywords."))
        return

    for inst in xs:
        await message.reply(instrument_to_markdown(inst), parse_mode=enums.ParseMode.MARKDOWN)


@app.on_callback_query
async def handle_button_click(client: PyrogramClient, callback_query: CallbackQuery):
    """Handler for button callbacks
    """

    data = callback_query.data
    if data.startswith("tracking_currency_confirmed>"):
        raise NotImplementedError("not yet done :D")

    if data.startswith("tracking_stock_confirmed>"):
        _, ticker_and_price, data_json = data.split(">")
        ticker, price = ticker_and_price.split("-")
        data_obj = json.loads(data_json)

        new_instrument = data_obj["new_instrument"]
        tracking = data_obj["tracking"]

        # if 'new_instrument' passed
        #   - we need to add new instrument to 'instruments' table
        #       and after that - add new 'tracking'
        if isinstance(new_instrument, dict):
            # insert new instrument to DB
            instrument_db_obj = add_instrument(new_instrument)
            if instrument_db_obj is None:
                await callback_query.answer(msg_error("Failed to add new tracking"))
                raise RuntimeError(
                    f"Failed to insert new instrument {new_instrument}")

            tracking["tracked_instrument"] = instrument_db_obj["id"]
            tracking_db_obj = add_tracking(tracking)

            if tracking_db_obj in None:
                await callback_query.answer(msg_error("Failed to add new tracking"))
                raise RuntimeError(f"Failed to insert new tracking {tracking}")

            await callback_query.answer(msg_ok(f"Added {ticker} notify on price: {price}"))
            return

        # if 'new_instrument' was not passed
        # (means that it's already added to table 'instruments')
        #   - so we only should add new 'tracking'
        tracking_obj = add_tracking(tracking)
        if tracking_obj in None:
            await callback_query.answer(msg_error("Failed to add new tracking"))
            raise RuntimeError(f"Failed to insert new tracking {tracking}")

        await callback_query.answer(msg_ok(f"Added {ticker} notify on price: {price}"))


# run the bot
if __name__ == "__main__":
    import asyncio
    print("Starting bot...")
    asyncio.run(app.run())
    print("Exiting bot...")
