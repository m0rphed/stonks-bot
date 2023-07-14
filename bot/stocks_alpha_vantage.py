import emoji
import creds
import datetime
from alpha_vantage.async_support.timeseries import TimeSeries as TimeSeriesAsync
from alpha_vantage.async_support.foreignexchange import ForeignExchange as ForeignExchangeAsync
from fin_instruments_dto import InstrumentInfo, StockInfo, CurrencyPairInfo

# Alpha Vantage API key
ALPHA_VANTAGE_KEY = creds.get_from_env(
    "ALPHA_VANTAGE_TOKEN", env_file_path="./secret/.env")


def _search_res_to_instrument_object(data: dict) -> InstrumentInfo:
    inst_dto = InstrumentInfo(
        symbol=data["1. symbol"],               # "MSF0.FRK"
        name=data["2. name"],                   # "MICROSOFT CORP. CDR"
        instrument_type=data["3. type"],        # "Equity"
        region=data["4. region"],               # "Frankfurt"
        market_open=data["5. marketOpen"],      # "08:00"
        market_close=data["6. marketClose"],    # "20:00"
        timezone=data["7. timezone"],           # "UTC+02"
        currency=data["8. currency"]            # "EUR"
    )

    return inst_dto


def _region_emoji_or_empty(reg_str: str) -> str:
    supported_regions = {"Frankfurt":           ":flag_for_Germany:",
                         "XETRA":               ":flag_for_Germany:",
                         "United States":       ":flag_for_United_States:",
                         "United Kingdom":      ":flag_for_United_Kingdom:",
                         "Brazil/Sao Paolo":    ":flag_for_Brazil:"}

    if reg_str not in supported_regions.keys():
        return ""

    return emoji.emojize(supported_regions[reg_str], language="alias")


def _make_datetime(str_with_datetime: str) -> datetime.datetime:
    # "%Y-%m-%d %H:%M:%S %z" # <-- TODO: should we handle timezone? or it's always UTC?
    _format = "%Y-%m-%d %H:%M:%S"
    return datetime.datetime.strptime(str_with_datetime, _format)


def _to_curr_pair_dto(data: dict) -> CurrencyPairInfo:
    curr_pair_dto = CurrencyPairInfo(
        code_from=data["1. From_Currency Code"],    # "USD"
        name_from=data["2. From_Currency Name"],    # "United States Dollar"

        code_to=data["3. To_Currency Code"],        # "EUR"
        name_to=data["4. To_Currency Name"],        # "Euro"
        rate=float(data["5. Exchange Rate"]),       # "0.89050000"
        last_datetime=_make_datetime(               # "2023-07-13 22:42:01" + " UTC"
            data["6. Last Refreshed"]
        ),
        tz=data["7. Time Zone"],                    # "UTC"
        price_bid=float(data["8. Bid Price"]),      # "0.89048000"
        price_ask=float(data["9. Ask Price"])       # "0.89053000"
    )

    return curr_pair_dto


def instrument_to_markdown(x: InstrumentInfo) -> str:
    text = f"**{x.name}**\n" \
        f"\n• --Code--: `{x.symbol}`," \
        f"\n• Instrument type: __{x.instrument_type.lower()}__" \
        f"\n• --Currency--: `{x.currency}`" \
        f"\n• Timezone: {x.timezone}" \
        f"\n• ⏰ from __{x.market_open}__ to __{x.market_close}__"

    reg_str = f"\n - region: {_region_emoji_or_empty(x.region)} {x.region}"
    return text + reg_str


async def get_search_results(query: str) -> list[InstrumentInfo] | None:
    try:
        ts = TimeSeriesAsync(key=ALPHA_VANTAGE_KEY)
        # run search query and retrieve matching instruments
        search_res, _ = await ts.get_symbol_search(query)
        await ts.close()
        return [_search_res_to_instrument_object(sr) for sr in search_res]

    except Exception as e:
        print("Error running search query:", str(e))
        return None


async def get_stock_info(ticker: str) -> StockInfo | None:
    try:
        # init alpha-vantage client for stock market data
        ts = TimeSeriesAsync(key=ALPHA_VANTAGE_KEY)
        # retrieve stock data by specified ticker symbol
        data, _ = await ts.get_quote_endpoint(symbol=ticker)
        await ts.close()

        exchange = "NASDAQ or NYSE"  # TODO: find out which :D

        # extract relevant information from the response
        # TODO: find a way to extract real company name from the API
        stock_real_name = data["01. symbol"]
        price = data["05. price"]
        per_day_price_delta_percentage = float(
            data["10. change percent"][:-1])

        return StockInfo(ticker, price, exchange, stock_real_name, per_day_price_delta_percentage)

    except Exception as e:
        print("Error retrieving stock data:", str(e))
        return None


async def get_curr_pair_info(from_curr: str, to_curr: str) -> CurrencyPairInfo | None:
    try:
        # init alpha-vantage client for foreign exchange data
        fx = ForeignExchangeAsync(key=ALPHA_VANTAGE_KEY)
        # retrieve currency exchange data
        data, _ = await fx.get_currency_exchange_rate(
            from_currency=from_curr, to_currency=to_curr)
        await fx.close()

        # TODO: find a way to retrieve daily change from API
        # per_day_price_delta_percentage = float(
        #     data["9. Percentage Price Change"][:-1])

        # extract relevant information from the response
        curr_pair = _to_curr_pair_dto(data)
        return curr_pair

    except Exception as e:
        print("Error retrieving currency data:", str(e))
        return None
