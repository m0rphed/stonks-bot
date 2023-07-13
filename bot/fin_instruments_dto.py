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
