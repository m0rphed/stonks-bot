import matplotlib.pyplot as plt
from datetime import datetime
from alpha_vantage.timeseries import TimeSeries
from creds import get_from_toml
from stocks_alpha_vantage import get_currency_pair_info, get_current_stock_info


def test_small():
    TICKER = "MSFT"

    alpha_vantage = get_from_toml("alpha-vantage")["token"]
    print(alpha_vantage)

    ts = TimeSeries(key=alpha_vantage, output_format="pandas")

    data, meta_data = ts.get_intraday(
        symbol=TICKER,
        interval="1min",
        outputsize="full"
    )

    data["4. close"].plot()
    plt.title("Intraday Times Series for the MSFT stock (1 min)")

    stamp = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')

    plt.savefig(f"./data/{TICKER}_{stamp}.png")
    print("figure saved!")


def test_functions():
    ticker_info = get_current_stock_info("MSFT")
    print(ticker_info)

    curr_info = get_currency_pair_info("USD", "JPY")
    print(curr_info)


if __name__ == "__main__":
    test_functions()
