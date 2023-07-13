import creds
from alpha_vantage.async_support.timeseries import TimeSeries as TimeSeriesAsync
from alpha_vantage.async_support.foreignexchange import ForeignExchange as ForeignExchangeAsync
from fin_instruments_dto import StockInfo, CurrencyInfo

# Alpha Vantage API key
ALPHA_VANTAGE_KEY = creds.get_from_env(
    "ALPHA_VANTAGE_TOKEN", env_file_path="./secret/.env")


async def get_stock_info(ticker: str) -> StockInfo | None:
    try:
        # init alpha-vantage client for stock market data
        ts = TimeSeriesAsync(key=ALPHA_VANTAGE_KEY)
        # retrieve stock data by specified ticker symbol
        data, _meta_data = await ts.get_quote_endpoint(symbol=ticker)
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


async def get_currency_pair_info(from_curr: str, to_curr: str) -> CurrencyInfo | None:
    try:
        # init alpha-vantage client for foreign exchange data
        fx = ForeignExchangeAsync(key=ALPHA_VANTAGE_KEY)
        # retrieve currency exchange data
        data, _ = await fx.get_currency_exchange_rate(
            from_currency=from_curr, to_currency=to_curr)
        await fx.close()

        # extract relevant information from the response
        curr_from_name = data["2. From_Currency Name"]
        curr_to_name = data["4. To_Currency Name"]
        rate = float(data["5. Exchange Rate"])

        # TODO: find a way to retrieve daily change from API
        # per_day_price_delta_percentage = float(
        #     data["9. Percentage Price Change"][:-1])

        return CurrencyInfo(curr_from_name, curr_to_name, rate)
    except Exception as e:
        print("Error retrieving currency data:", str(e))
        return None
