import datetime
from enum import unique, StrEnum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


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


class UserEntity(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime.datetime
    tg_user_id: int
    settings: dict | None


@unique
class InstrumentType(StrEnum):
    sm_instrument = "stock_market_instrument"
    curr_pair = "currency_exchange_pair"
    crypto_pair = "crypto_exchange_pair"


class InstrumentEntity(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    updated_at: datetime.datetime
    symbol: str
    figi_code: str | None
    price: float | None
    exchange_rate: float | None
    data_provider_code: str
    type: InstrumentType


class TrackingEntity(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime.datetime
    instrument: UUID = Field(default_factory=uuid4)
    tracked_by: UUID = Field(default_factory=uuid4)
    on_price: float | None
    on_rate: float | None
    notify_daily_at: Optional[datetime.datetime]
