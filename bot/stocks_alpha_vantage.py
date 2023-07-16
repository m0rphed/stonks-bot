import emoji
import creds

from alpha_vantage.async_support.timeseries import TimeSeries as TimeSeriesAsync
from alpha_vantage.async_support.foreignexchange import ForeignExchange as ForeignExchangeAsync
from api_models import InstrumentSearchInfo, StockInfo, CurrencyPairInfo

# Alpha Vantage API key
ALPHA_VANTAGE_KEY = creds.get_from_env(
    "ALPHA_VANTAGE_TOKEN", env_file_path="./secret/.env")


def _region_emoji_or_empty(reg_str: str) -> str:
    supported_regions = {"Frankfurt":           ":flag_for_Germany:",
                         "XETRA":               ":flag_for_Germany:",
                         "United States":       ":flag_for_United_States:",
                         "United Kingdom":      ":flag_for_United_Kingdom:",
                         "Brazil/Sao Paolo":    ":flag_for_Brazil:"}

    if reg_str not in supported_regions.keys():
        return ""

    return emoji.emojize(supported_regions[reg_str], language="alias")


def instrument_to_markdown(x: InstrumentSearchInfo) -> str:
    text = f"**{x.name}**\n" \
        f"\n• --Code--: `{x.symbol}`," \
        f"\n• Instrument type: __{x.instrument_type.lower()}__" \
        f"\n• --Currency--: `{x.currency}`" \
        f"\n• Timezone: {x.timezone}" \
        f"\n• ⏰ from __{x.market_open}__ to __{x.market_close}__"

    reg_str = f"\n - region: {_region_emoji_or_empty(x.region)} {x.region}"
    return text + reg_str


async def get_search_results(query: str) -> list[InstrumentSearchInfo] | None:
    try:
        ts = TimeSeriesAsync(key=ALPHA_VANTAGE_KEY)
        # run search query and retrieve matching instruments
        search_res, _ = await ts.get_symbol_search(query)
        await ts.close()

        return [InstrumentSearchInfo.parse_obj(sr) for sr in search_res]

    except Exception as e:
        print("Error running search query:", str(e))
        return None


async def get_stock_info(ticker: str) -> StockInfo | None:
    try:
        # init alpha-vantage client for stock market data
        ts = TimeSeriesAsync(key=ALPHA_VANTAGE_KEY)
        # retrieve stock data by specified ticker symbol
        resp, _ = await ts.get_quote_endpoint(symbol=ticker)
        await ts.close()

        stock_obj = StockInfo.parse_obj(resp)
        # TODO: find out which US exchange: "NASDAQ" or "NYSE"
        stock_obj.exchange = "NASDAQ"

        return stock_obj

    except Exception as e:
        print(f"Error retrieving stock data for '{ticker}':", str(e))
        return None


async def get_curr_pair_info(from_curr: str, to_curr: str) -> CurrencyPairInfo | None:
    try:
        # init alpha-vantage client for foreign exchange data
        fx = ForeignExchangeAsync(key=ALPHA_VANTAGE_KEY)
        # retrieve currency exchange data by symbols: "USD", "CNY"
        resp, _ = await fx.get_currency_exchange_rate(from_curr, to_curr)
        await fx.close()

        # TODO: find a way to retrieve daily change from API
        # per_day_price_delta_percentage: float = ...
        return CurrencyPairInfo.parse_obj(resp)

    except Exception as e:
        print(
            f"Error retrieving currency pair data "
            "for '{from_curr} to {to_curr}':", str(e))
        return None
