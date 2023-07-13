from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.foreignexchange import ForeignExchange
import creds

from fin_instruments_dto import StockInfo, CurrencyInfo

# Alpha Vantage API key
ALPHA_VANTAGE_KEY = creds.get_from_env("ALPHA_VANTAGE_TOKEN")

# Initialize Alpha Vantage clients
ts = TimeSeries(key=ALPHA_VANTAGE_KEY)
fx = ForeignExchange(key=ALPHA_VANTAGE_KEY)


async def get_stock_info(ticker: str) -> StockInfo | None:
    try:
        # Retrieve stock data
        data, _meta_data = await ts.get_quote_endpoint(symbol=ticker)

        exchange = "NASDAQ or NYSE"  # TODO: find out which :D

        # Extract relevant information from the response
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
        # retrieve currency exchange data
        data, _ = await fx.get_currency_exchange_rate(
            from_currency=from_curr, to_currency=to_curr)

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
