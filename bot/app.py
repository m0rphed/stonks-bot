from pyrogram import filters, Client as PyrogramClient
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from pyrogram import enums
from bot_callback_funcs import finish_callback_query, tracking_cancellation
from bot_helpers import get_random_key

import creds
from formatting import msg_ok, msg_warning, msg_error

from models import BotUserEntity, CurrencyPairInfo, InstrumentEntity, InstrumentSearchInfo, StockInfo
from api_alpha_vantage import get_curr_pair_info, get_stock_info, get_search_results, instrument_to_markdown

from db_funcs import get_supabase_client
from supabase_funcs import add_instrument, add_user_by_id, check_instrument_by_ticker, check_user, check_curr_pair, add_tracking

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

callback_data_dict: dict = {}


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
    stock_db_obj: InstrumentEntity | None = check_instrument_by_ticker(
        ticker, "alpha_vantage")

    if stock_db_obj is not None:
        tracking = {
            "tracked_instrument": str(stock_db_obj.id),
            "tracked_by_user": str(user_db_obj.id),
            "notify": "on_change",
            "on_price": float(price_to_be_reached)
        }

        # create reply message with stock info from db
        reply_message = f"Stock information:\n\n" \
                        f"Ticket: {stock_db_obj.ticker}\n" \
                        f"Price: {stock_db_obj.price}\n" \
                        f"Exchange: {stock_db_obj.code_exchange}\n" \
                        f"• provided by 👉 `alpha_vantage`\n" \
                        f"\nIf this is the correct stock you want to track, click the button below to confirm."

    # if not found in "instruments" -> try retrieve from API
    else:
        # retrieve stock info using get_stock_info
        stock_api: StockInfo | None = await get_stock_info(ticker)
        if stock_api is None:
            await message.reply(
                msg_error(
                    f"Failed to retrieve stock data by provided symbol: {ticker}.\n"
                    "Try searching stocks with command '/search_stock <ticker>' first."
                )
            )
            return

        # prepare fields of new instrument that to be inserted to the table
        new_stock = {
            "is_curr_pair": False,
            "is_crypto_pair": False,
            "data_provider": "alpha_vantage",
            "price": stock_api.price,
            "code_exchange": stock_api.exchange,
            "ticker": stock_api.symbol
        }

        tracking = {
            # link to the new instrument we are gonna insert
            "tracked_instrument": "",
            # TODO: find a better way to encode UUID instance in models
            "tracked_by_user": str(user_db_obj.id),
            "notify": "on_change",
            "on_price": float(price_to_be_reached)
        }

        # create reply message with stock info from API
        reply_message = f"Stock information:\n\n" \
                        f"Ticket: {stock_api.symbol}\n" \
                        f"Price: {stock_api.price}\n" \
                        f"Exchange: {stock_api.exchange}\n" \
                        f"Change: {stock_api.change}\n" \
                        f"Percentage change: {stock_api.change_percent}\n"\
                        "• provided by 👉 `alpha_vantage`\n" \
                        f"\nIf this is the correct stock you want to track, click the button below to confirm."

    # prepare data to pass to the callback query via placing it into a dict by generated key
    instrument = "" if new_stock is None else new_stock
    key: str = get_random_key()
    callback_data_dict[key] = {
        "new_instrument": instrument,
        "tracking": tracking
    }

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Confirm", callback_data=f"tracking_stock_confirmed>{ticker}-{price_to_be_reached}>{key}"
                ),
                InlineKeyboardButton(
                    "Cancel", callback_data=f"tracking_stock_canceled>{key}"
                )
            ]
        ]
    )

    await message.reply_text(
        reply_message,
        reply_markup=keyboard,
        parse_mode=enums.ParseMode.MARKDOWN
    )


@app.on_message(filters.command("track_currency"))
async def track_currency(client: PyrogramClient, message: Message):
    """adds tracking of a currency pair: "/track_currency <from currency symbol> <to currency symbol>"
    example:
        /track USD EUR
        /track BTC USD
    """
    user_db_obj: BotUserEntity | None = await authenticated_users_only(
        tg_user_id=message.from_user.id,
        chat_id=message.chat.id
    )

    if user_db_obj is None:
        return

    args = message.text.split()[1:]
    if len(args) != 3:
        await message.reply(
            msg_error(
                "Please provide a currency pair symbols and target rate.")
        )
        return

    from_curr_str, to_curr_str, target_rate = args
    try:
        # exception would be raised
        # if string could not be converted to valid float value
        rate_to_be_reached = float(target_rate)
    except ValueError:
        await message.reply(
            msg_error(
                f"Rate you provided: '{rate_to_be_reached}'\n"
                "- Please provide a valid rate value"
                " e.g. 👉 1.5, 0.019")
        )
        return

    new_curr_pair: None | dict = None
    tracking: None | dict = None
    reply_message: None | str = None

    # check if curr pair is tracked by anyone
    # (which means that its `curr_code` exist in the "instruments" table)
    curr_pair_db_obj: InstrumentEntity | None = check_curr_pair(
        from_curr_str,
        to_curr_str,
        "alpha_vantage"
    )

    if curr_pair_db_obj is not None:
        tracking = {
            "tracked_instrument": str(curr_pair_db_obj.id),
            "tracked_by_user": str(user_db_obj.id),
            "notify": "on_change",
            "on_rate": float(rate_to_be_reached)
        }

        # create reply message with exchange pair info from db
        reply_message = f"Currency exchange pair information:\n\n" \
                        f"From -> to: {curr_pair_db_obj.code_curr}\n" \
                        f"Price: {curr_pair_db_obj.price}\n" \
                        f"Exchange rate: {curr_pair_db_obj.exchange_rate}\n"\
                        f"Exchange: {curr_pair_db_obj.code_exchange}\n" \
                        "• provided by 👉 `alpha_vantage`\n" \
                        f"\nIf this is the correct exchange pair you want to track, click the button below to confirm."

    # if not found in "instruments" -> try retrieve from API
    else:
        # retrieve currency pair exchange rate from API
        curr_pair_api: CurrencyPairInfo | None = await get_curr_pair_info(from_curr_str, to_curr_str)
        if curr_pair_api is None:
            await message.reply(
                msg_error(
                    f"Failed to retrieve currency pair → from '{from_curr_str}' to '{to_curr_str}'."
                    "Try providing different currency symbol e.g. 👉"
                    "\n\t/track_currency USD CNY"
                    "\n\t/track_currency BTC USD"
                )
            )
            return

        # prepare fields of new instrument that to be inserted to the table
        new_curr_pair = {
            "is_curr_pair": True,
            "is_crypto_pair": False,
            "data_provider": "alpha_vantage",
            "price": curr_pair_api.price_bid,  # TODO: should it be BID PRICE or ASK PRICE???
            "code_curr": str(curr_pair_api.code_from) + "_" + str(curr_pair_api.code_to)
        }

        tracking = {
            # link to the new instrument we are gonna insert
            "tracked_instrument": "",
            # TODO: find a better way to encode UUID instance in models
            "tracked_by_user": str(user_db_obj.id),
            "notify": "on_change",
            "on_rate": float(rate_to_be_reached)
        }

        # create reply message with exchange pair info from API
        reply_message = f"Currency exchange pair information:\n\n" \
                        f"**{curr_pair_api.name_from}** 👉 **{curr_pair_api.name_to}**\n" \
                        f"`{curr_pair_api.code_from}` 👉 `{curr_pair_api.code_to}`\n" \
                        f"Price bid: {curr_pair_api.price_bid}\n"\
                        f"Price ask: {curr_pair_api.price_ask}\n"\
                        f"Exchange rate: {curr_pair_api.rate}\n"\
                        "• provided by 👉 `alpha_vantage`\n" \
                        f"\nIf this is the correct exchange pair you want to track, click the button below to confirm."

    # prepare data to pass to the callback query via placing it into a dict by generated key
    instrument = "" if new_curr_pair is None else new_curr_pair
    key: str = get_random_key()
    callback_data_dict[key] = {
        "new_instrument": instrument,
        "tracking": tracking
    }

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Confirm", callback_data=f"tracking_curr_confirmed>{from_curr_str}-{to_curr_str}-{rate_to_be_reached}>{key}"
                ),
                InlineKeyboardButton(
                    "Cancel", callback_data=f"tracking_curr_canceled>{key}"
                )
            ]
        ]
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


@app.on_callback_query()
async def handle_button_click(client: PyrogramClient, callback_query: CallbackQuery):
    """Handler for button callbacks
    """

    data = callback_query.data

    if data.startswith("tracking_curr_confirmed>"):
        _, symbols_and_rate, cb_dict_key = data.split(">")
        from_symbol, to_symbol, rate = symbols_and_rate.split("-")
        data_obj = callback_data_dict[cb_dict_key]

        new_instrument = data_obj["new_instrument"]
        tracking = data_obj["tracking"]

        # if 'new_instrument' passed
        #   - we need to add new instrument to 'instruments' table
        #       and after that - add new 'tracking'
        if isinstance(new_instrument, dict):
            # insert new instrument to DB
            instrument_db_obj = add_instrument(new_instrument)
            if instrument_db_obj is None:
                await finish_callback_query(
                    callback_query,
                    msg_text=msg_error("Failed to add new tracking"),
                    delete_prev=True
                )
                # TODO: log: RuntimeError(f"Failed to insert new instrument {new_instrument}")
                return

            tracking["tracked_instrument"] = instrument_db_obj["id"]
            tracking_db_obj = add_tracking(tracking)

            if tracking_db_obj in None:
                await finish_callback_query(
                    callback_query,
                    msg_text=msg_error("Failed to add new tracking"),
                    delete_prev=True
                )
                # TODO: log: RuntimeError(f"Failed to insert new tracking {tracking}")
                return

            await finish_callback_query(
                callback_query,
                msg_text=msg_ok(
                    f"Added {from_symbol}-{to_symbol} notify on rate: {rate}"),
                delete_prev=True
            )
            return

        # if 'new_instrument' was not passed
        # (means that it's already added to table 'instruments')
        #   - so we only should add new 'tracking'
        tracking_obj = add_tracking(tracking)
        if tracking_obj in None:
            await finish_callback_query(
                callback_query,
                msg_text=msg_error("Failed to add new tracking"),
                delete_prev=True
            )
            # TODO: log RuntimeError(f"Failed to insert new tracking {tracking}")
            return

        await finish_callback_query(
            callback_query,
            msg_text=msg_ok(
                f"Added {from_symbol}-{to_symbol} notify on rate: {rate}"),
            delete_prev=True
        )
        return

    if data.startswith("tracking_stock_confirmed>"):
        _, symbols_and_rate, cb_dict_key = data.split(">")
        ticker, price = symbols_and_rate.split("-")
        data_obj = callback_data_dict[cb_dict_key]

        new_instrument = data_obj["new_instrument"]
        tracking = data_obj["tracking"]

        # if 'new_instrument' passed
        #   - we need to add new instrument to 'instruments' table
        #       and after that - add new 'tracking'
        if isinstance(new_instrument, dict):
            # insert new instrument to DB
            instrument_db_obj = add_instrument(new_instrument)
            if instrument_db_obj is None:
                await finish_callback_query(
                    callback_query,
                    msg_text=msg_error("Failed to add new tracking"),
                    delete_prev=True
                )
                # TODO: log: RuntimeError(f"Failed to insert new instrument {new_instrument}")
                return

            tracking["tracked_instrument"] = instrument_db_obj["id"]
            tracking_db_obj = add_tracking(tracking)

            if tracking_db_obj in None:
                await finish_callback_query(
                    callback_query,
                    msg_text=msg_error("Failed to add new tracking"),
                    delete_prev=True
                )
                # TODO: log: RuntimeError(f"Failed to insert new tracking {tracking}")
                return

            await finish_callback_query(
                callback_query,
                msg_text=msg_ok(f"Added {ticker} notify on price: {price}"),
                delete_prev=True
            )
            return

        # if 'new_instrument' was not passed
        # (means that it's already added to table 'instruments')
        #   - so we only should add new 'tracking'
        tracking_obj = add_tracking(tracking)
        if tracking_obj in None:
            await finish_callback_query(
                callback_query,
                msg_text=msg_error("Failed to add new tracking"),
                delete_prev=True
            )
            # TODO: log RuntimeError(f"Failed to insert new tracking {tracking}")
            return

        await finish_callback_query(
            callback_query,
            msg_text=msg_ok(f"Added {ticker} notify on price: {price}"),
            delete_prev=True
        )
        return

    if data.startswith("tracking_curr_canceled>"):
        _, key = data.split(">")
        callback_data_dict.pop(key)
        await tracking_cancellation(callback_query, callback_data_dict)
        return

    if data.startswith("tracking_stock_canceled>"):
        _, key = data.split(">")
        callback_data_dict.pop(key)
        await tracking_cancellation(callback_query, callback_data_dict)
        return

# run the bot
if __name__ == "__main__":
    import asyncio
    print("Starting bot...")
    asyncio.run(app.run())
    print("Exiting bot...")
