import matplotlib.pyplot as plt
from datetime import datetime
from alpha_vantage.timeseries import TimeSeries
from creds import get_from_toml


if __name__ == "__main__":
    TICKET = "MSFT"

    alpha_vantage = get_from_toml("alpha-vantage")["token"]
    print(alpha_vantage)

    ts = TimeSeries(key=alpha_vantage, output_format="pandas")

    data, meta_data = ts.get_intraday(
        symbol=TICKET,
        interval="1min",
        outputsize="full"
    )

    data["4. close"].plot()
    plt.title("Intraday Times Series for the MSFT stock (1 min)")

    stamp = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')

    plt.savefig(f"./data/{TICKET}_{stamp}.png")
    print("figure saved!")
