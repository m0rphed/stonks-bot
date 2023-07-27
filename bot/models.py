import datetime as dt
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field


class InstrumentSearchInfo(BaseModel):  # Instrument search result fields:
    symbol: str                         = Field(alias="1. symbol")
    name: str                           = Field(alias="2. name")
    instrument_type: str                = Field(alias="3. type")
    region: str                         = Field(alias="4. region")
    market_open: str                    = Field(alias="5. marketOpen")
    market_close: str                   = Field(alias="6. marketClose")
    timezone: str                       = Field(alias="7. timezone")
    currency: str                       = Field(alias="8. currency")


class CurrencyPairInfo(BaseModel):      # ForEx pair fields:
    code_from: str                      = Field(alias="1. From_Currency Code")
    name_from: str                      = Field(alias="2. From_Currency Name")
    code_to: str                        = Field(alias="3. To_Currency Code")
    name_to: str                        = Field(alias="4. To_Currency Name")
    rate: float                         = Field(alias="5. Exchange Rate")
    last_refreshed: dt.datetime         = Field(alias="6. Last Refreshed")
    timezone: str                       = Field(alias="7. Time Zone")
    price_bid: float                    = Field(alias="8. Bid Price")
    price_ask: float                    = Field(alias="9. Ask Price")
    exchange: Optional[str]             # TODO: define alias for this field
    data_provider: Optional[str]        # TODO: define alias for this field


class StockInfo(BaseModel):             # Stock fields:
    symbol: str                         = Field(alias="01. symbol")
    price_open: float                   = Field(alias="02. open")
    price_high: float                   = Field(alias="03. high")
    price_low: float                    = Field(alias="04. low")
    price: float                        = Field(alias="05. price")
    volume: int | float                 = Field(alias="06. volume")
    latest_trading_day: dt.date         = Field(alias="07. latest trading day")
    prev_close: float                   = Field(alias="08. previous close")
    change: float                       = Field(alias="09. change")
    change_percent: str                 = Field(alias="10. change percent")
    exchange: Optional[str]             # TODO: define alias for this field
    data_provider: Optional[str]        # TODO: define alias for this field


class CryptoPairInfo(BaseModel):        # fields are similar to CurrencyPairInfo
    code_from: str                      = Field(alias="1. From_Currency Code")
    name_from: str                      = Field(alias="2. From_Currency Name")
    code_to: str                        = Field(alias="3. To_Currency Code")
    name_to: str                        = Field(alias="4. To_Currency Name")
    rate: float                         = Field(alias="5. Exchange Rate")
    last_refreshed: dt.datetime         = Field(alias="6. Last Refreshed")
    timezone: str                       = Field(alias="7. Time Zone")
    price_bid: float                    = Field(alias="8. Bid Price")
    price_ask: float                    = Field(alias="9. Ask Price")
    exchange: Optional[str]             # TODO: define alias for this field
    data_provider: Optional[str]        # TODO: define alias for this field


# models for db entities
class BotUserEntity(BaseModel):
    id: UUID
    created_at: dt.datetime
    tg_user_id: int
    email: Optional[str]
    password: Optional[str]
    tinkoff_token: Optional[str]
    tinkoff_sandbox: Optional[str]
    settings: Optional[dict]


class InstrumentEntity(BaseModel):
    id: UUID
    updated_at: dt.datetime
    code_figi: Optional[str]
    code_exchange: Optional[str]
    ticker: Optional[str]
    price: Optional[float] = None
    exchange_rate: Optional[float] = None
    code_curr: Optional[str]
    is_curr_pair: bool
    is_crypto_pair: bool
    data_provider: str


class TrackingEntity(BaseModel):
    id: UUID
    tracked_instrument: UUID
    tracked_by_user: UUID
    on_rate: Optional[float]
    on_price: Optional[float]
    notify: str


def create_tracking_obj(instrument: InstrumentEntity, by_user: BotUserEntity, notify: str = "on_change") -> TrackingEntity:
    tracking = {}
    tracking["tracked_instrument"]  = instrument.id
    tracking["tracked_by_user"]     = by_user.id
    tracking["on_rate"]             = None if instrument.exchange_rate is None else instrument.exchange_rate
    tracking["on_price"]            = None if instrument.price is None else instrument.price
    tracking["notify"]              = notify
    return TrackingEntity.parse_obj(tracking)
