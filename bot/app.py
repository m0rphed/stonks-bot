import creds
from pyrogram import Client as PyrogramClient
from pyrogram import enums, filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message
)
from api_alpha_vantage import (
    get_curr_pair_info,
    get_search_results,
    get_stock_info,
    instrument_to_markdown
)
from bot_callback_funcs import finish_callback_query, tracking_cancellation
from bot_helpers import authenticated_users_only, get_random_key
from formatting import (
    curr_pair_api_confirmation,
    curr_pair_entity_confirmation,
    msg_error,
    msg_warning,
    msg_ok,
    stock_api_confirmation,
    stock_entity_confirmation
)
from models import (
    BotUserEntity,
    CurrencyPairInfo,
    InstrumentEntity,
    InstrumentSearchInfo,
    StockInfo
)
from supabase_funcs import (
    add_instrument,
    add_tracking,
    add_user_by_id,
    check_curr_pair,
    check_instrument_by_ticker,
    check_user
)

BOT_NAME = "stonks-bot"
# TODO: impl. enums for data providers for supported APIs
DEFAULT_DATA_PROVIDER = "alpha_vantage"

# ensure needed environment variables are loaded
creds.load_env_file("./secret/.env")

# set telegram client credentials
app = PyrogramClient(
    BOT_NAME,
    api_id=creds.get_from_env("TELEGRAM_API_API_ID"),
    api_hash=creds.get_from_env("TELEGRAM_API_API_HASH"),
    bot_token=creds.get_from_env("TELEGRAM_BOT_TOKEN")
)

# hotfix: dictionary to store data to use in callback function that is too large to pass via callback
cb_data_dict: dict = {}


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
    user_entity: BotUserEntity | None = await authenticated_users_only(message)

    if user_entity is None:
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
    stock_entity: InstrumentEntity | None = check_instrument_by_ticker(
        ticker, "alpha_vantage")

    if stock_entity is not None:
        tracking = {
            "tracked_instrument": str(stock_entity.id),
            "tracked_by_user": str(user_entity.id),
            "notify": "on_change",
            "on_price": float(price_to_be_reached)
        }

        # create reply message with stock info from db
        reply_message = stock_entity_confirmation(stock_entity)

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
            "tracked_by_user": str(user_entity.id),
            "notify": "on_change",
            "on_price": float(price_to_be_reached)
        }

        # create reply message with stock info from API
        reply_message = stock_api_confirmation(stock_api)

    # prepare data to pass to the callback query via placing it into a dict by generated key
    instrument = "" if new_stock is None else new_stock
    key: str = get_random_key()
    cb_data_dict[key] = {
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
    user_entity: BotUserEntity | None = await authenticated_users_only(message)

    if user_entity is None:
        return

    args = message.text.split()[1:]
    if len(args) != 3:
        await message.reply(msg_error("Please provide a curr. exchange pair symbols and target rate."))
        return

    crp_from, crp_to, target_rate = args
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
    crp_entity: InstrumentEntity | None = check_curr_pair(
        crp_from,
        crp_to,
        "alpha_vantage"
    )

    if crp_entity is not None:
        tracking = {
            "tracked_instrument": str(crp_entity.id),
            "tracked_by_user": str(user_entity.id),
            "notify": "on_change",
            "on_rate": float(rate_to_be_reached)
        }

        # create reply message with exchange pair info from db
        reply_message = curr_pair_entity_confirmation(crp_entity)

    # if not found in "instruments" -> try retrieve from API
    else:
        # retrieve currency pair exchange rate from API
        crp_api: CurrencyPairInfo | None = await get_curr_pair_info(crp_from, crp_to)
        if crp_api is None:
            await message.reply(
                msg_error(
                    f"Failed to retrieve currency pair → from '{crp_from}' to '{crp_to}'."
                    "Try providing different currency symbol e.g. 👉"
                    "\n\t`/track_currency USD CNY <rate>`"
                    "\n\t`/track_currency BTC USD <rate>`"
                ),
                parse_mode=enums.ParseMode.MARKDOWN
            )
            return

        # prepare fields of new instrument that to be inserted to the table
        new_curr_pair = {
            "is_curr_pair": True,
            "is_crypto_pair": False,
            "data_provider": "alpha_vantage",
            "price": crp_api.price_bid,  # TODO: should it be BID PRICE or ASK PRICE???
            "code_curr": str(crp_api.code_from) + "_" + str(crp_api.code_to)
        }

        tracking = {
            # link to the new instrument we are gonna insert
            "tracked_instrument": "",
            # TODO: find a better way to encode UUID instance in models
            "tracked_by_user": str(user_entity.id),
            "notify": "on_change",
            "on_rate": float(rate_to_be_reached)
        }

        # create reply message with exchange pair info from API
        reply_message = curr_pair_api_confirmation(crp_api)

    # prepare data to pass to the callback query via placing it into a dict by generated key
    instrument = "" if new_curr_pair is None else new_curr_pair
    key: str = get_random_key()
    cb_data_dict[key] = {
        "new_instrument": instrument,
        "tracking": tracking
    }

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Confirm", callback_data=f"tracking_curr_confirmed>{crp_from}-{crp_to}-{rate_to_be_reached}>{key}"
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
async def handle_button_click(client: PyrogramClient, cbq: CallbackQuery):
    """Handler for button callbacks
    """

    data = cbq.data
    if data.startswith("tracking_curr_confirmed>"):
        _, codes_and_rate, cb_dict_key = data.split(">")
        symbol_from, symbol_to, rate = codes_and_rate.split("-")
        data_obj = cb_data_dict[cb_dict_key]

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
                    cbq,
                    msg_text=msg_error("Failed to add new tracking"),
                    delete_prev_msg=True
                )
                # TODO: log: RuntimeError(f"Failed to insert new instrument {new_instrument}")
                return

            tracking["tracked_instrument"] = instrument_db_obj["id"]
            tracking_db_obj = add_tracking(tracking)

            if tracking_db_obj in None:
                await finish_callback_query(
                    cbq,
                    msg_text=msg_error("Failed to add new tracking"),
                    delete_prev_msg=True
                )
                # TODO: log: RuntimeError(f"Failed to insert new tracking {tracking}")
                return

            await finish_callback_query(
                cbq,
                msg_text=msg_ok(
                    f"Added {symbol_from}-{symbol_to} notify on rate: {rate}"),
                delete_prev_msg=True
            )
            return

        # if 'new_instrument' was not passed
        # (means that it's already added to table 'instruments')
        #   - so we only should add new 'tracking'
        tracking_obj = add_tracking(tracking)
        if tracking_obj in None:
            await finish_callback_query(
                cbq,
                msg_text=msg_error("Failed to add new tracking"),
                delete_prev_msg=True
            )
            # TODO: log RuntimeError(f"Failed to insert new tracking {tracking}")
            return

        await finish_callback_query(
            cbq,
            msg_text=msg_ok(
                f"Added {symbol_from}-{symbol_to} notify on rate: {rate}"),
            delete_prev_msg=True
        )
        return

    if data.startswith("tracking_stock_confirmed>"):
        _, codes_and_rate, cb_dict_key = data.split(">")
        ticker, price = codes_and_rate.split("-")
        data_obj = cb_data_dict[cb_dict_key]

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
                    cbq,
                    msg_text=msg_error("Failed to add new tracking"),
                    delete_prev_msg=True
                )
                # TODO: log: RuntimeError(f"Failed to insert new instrument {new_instrument}")
                return

            tracking["tracked_instrument"] = instrument_db_obj["id"]
            tracking_db_obj = add_tracking(tracking)

            if tracking_db_obj in None:
                await finish_callback_query(
                    cbq,
                    msg_text=msg_error("Failed to add new tracking"),
                    delete_prev_msg=True
                )
                # TODO: log: RuntimeError(f"Failed to insert new tracking {tracking}")
                return

            await finish_callback_query(
                cbq,
                msg_text=msg_ok(f"Added {ticker} notify on price: {price}"),
                delete_prev_msg=True
            )
            return

        # if 'new_instrument' was not passed
        # (means that it's already added to table 'instruments')
        #   - so we only should add new 'tracking'
        tracking_obj = add_tracking(tracking)
        if tracking_obj in None:
            await finish_callback_query(
                cbq,
                msg_text=msg_error("Failed to add new tracking"),
                delete_prev_msg=True
            )
            # TODO: log RuntimeError(f"Failed to insert new tracking {tracking}")
            return

        await finish_callback_query(
            cbq,
            msg_text=msg_ok(f"Added {ticker} notify on price: {price}"),
            delete_prev_msg=True
        )
        return

    if data.startswith("tracking_curr_canceled>"):
        _, key = data.split(">")
        cb_data_dict.pop(key)
        await tracking_cancellation(cbq, cb_data_dict)
        return

    if data.startswith("tracking_stock_canceled>"):
        _, key = data.split(">")
        cb_data_dict.pop(key)
        await tracking_cancellation(cbq, cb_data_dict)
        return

# run the bot
if __name__ == "__main__":
    import asyncio
    print("Starting bot...")
    asyncio.run(app.run())
    print("Exiting bot...")
