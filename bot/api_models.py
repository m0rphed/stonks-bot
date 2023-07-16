import datetime as dt
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
    exchange: Optional[str]             # TODO: define aliases for this field


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
