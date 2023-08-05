import datetime
import uuid
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Json


class User:  # abstract user
    pass


class StockMarketInstrument(BaseModel):  # may contain a stock, bonds, or any other instrument data
    symbol: str
    price: float
    data_provider: str
    exchange: Optional[str]


class ExchangePair(BaseModel):  # cryptocurrency exchange pair or fiat currency exchange pair
    code_from: str
    code_to: str
    rate: float
    name_from: Optional[str]
    name_to: Optional[str]
    data_provider: str
    exchange: Optional[str]


class SearchQueryRes(BaseModel):  # search query result
    symbol: str
    name: str
    instrument_type: str
    data_provider: str
    region: Optional[str]
    currency: Optional[str]

    def to_markdown(self) -> str:
        reg = f"\n• 🌎 Region: {self.region}" if self.region else ""
        curr = f"\n• 💸 --Currency--: `{self.currency}`" if self.currency else ""
        md_str = f"**{self.name}**\n" \
                 f"\n• --Symbol--: `{self.symbol}`" \
                 f"\n• Type: __{self.instrument_type}__" \
                 f"\n• Data provider: `{self.data_provider}`" + reg + curr

        return md_str


class UserEntity:
    id: uuid.UUID
    created_at: datetime.datetime
    tg_user_id: int
    settings: Optional[Json]


class InstrumentType(str, Enum):
    stock_market_instrument = 'stock_market_instrument'
    currency_exchange_pair = 'currency_exchange_pair'
    crypto_exchange_pair = 'crypto_exchange_pair'


class InstrumentEntity:
    id: uuid.UUID
    updated_at: datetime.datetime
    symbol: str
    figi_code: Optional[str]
    price: Optional[str]
    exchange_rate: Optional[str]
    data_provider_code: str
    type: InstrumentType


class TrackingEntity:
    id: uuid.UUID
    created_at: datetime.datetime
    instrument: uuid.UUID
    tracked_by: uuid.UUID
    on_price: Optional[float]
    on_rate: Optional[float]
    notify_daily_at: Optional[datetime.datetime]
