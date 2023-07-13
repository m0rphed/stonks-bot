from dataclasses import dataclass


@dataclass
class StockInfo:
    ticker: str
    price: str
    exchange: str
    stock_real_name: str
    per_day_price_delta_percentage: float


@dataclass
class CurrencyInfo:
    currency_from: str
    currency_to: str
    rate: float
    per_day_price_delta_percentage: float | None = None


@dataclass(frozen=True)
class InstrumentInfo:
    symbol: str
    name: str
    instrument_type: str
    region: str
    market_open: str
    market_close: str
    timezone: str
    currency: str


@dataclass
class CryptoInfo:
    pass


def get_crypto(symbol: str, market: str) -> CryptoInfo | None:
    pass
