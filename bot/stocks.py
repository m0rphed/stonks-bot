import creds
import asyncio
import matplotlib.pyplot as plt

from datetime import datetime

from stocks_alpha_vantage import get_search_results, get_curr_pair_info, get_stock_info
from alpha_vantage.async_support.timeseries import TimeSeries as TimeSeriesAsync

ALPHA_VANTAGE_KEY = creds.get_from_env(
    "ALPHA_VANTAGE_TOKEN", env_file_path="./secret/.env")


def test_small_sync():
    from alpha_vantage.timeseries import TimeSeries
    TICKER = "MSFT"

    alpha_vantage = creds.get_from_toml("alpha-vantage")["token"]
    print(alpha_vantage)

    ts = TimeSeries(key=alpha_vantage, output_format="pandas")
    data, _meta_data = ts.get_intraday(
        symbol=TICKER,
        interval="1min",
        outputsize="full"
    )

    data["4. close"].plot()
    plt.title("Intraday Times Series for the MSFT stock (1 min)")

    stamp = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
    plt.savefig(f"./data/{TICKER}_{stamp}.png")
    print("figure saved!")


async def test_data_retrieval():
    ticker_info = await get_stock_info("MSFT")
    print(ticker_info)

    curr_info = await get_curr_pair_info("USD", "JPY")
    print(curr_info)


async def get_data(symbol):
    ts = TimeSeriesAsync(key=ALPHA_VANTAGE_KEY)
    data, _ = await ts.get_quote_endpoint(symbol)
    await ts.close()
    return data


def run_simple_test():
    symbols = ['AAPL', 'GOOG', 'TSLA', 'MSFT']

    loop = asyncio.get_event_loop()
    tasks = [get_data(symbol) for symbol in symbols]
    group1 = asyncio.gather(*tasks)

    results = loop.run_until_complete(group1)
    loop.close()

    for res in results:
        print(res)


def run_test_retrieval():
    loop = asyncio.get_event_loop()
    group1 = asyncio.gather(test_data_retrieval())
    loop.run_until_complete(group1)
    loop.close()


async def test_symbol_search(text: str):
    instruments = await get_search_results(text)
    for i in instruments:
        print(i)


if __name__ == "__main__":
    # test_small_sync()
    # run_simple_test()
    # asyncio.run(test_data_retrieval())
    # asyncio.run(test_symbol_search("Microsoft"))
    asyncio.run(get_curr_pair_info("ETH", "RUB"))