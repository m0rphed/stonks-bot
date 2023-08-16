import datetime as dt
from typing import Optional

from pydantic import Field, field_validator

from tg_stonks.providers.models import (
    StockMarketInstrument,
    SearchQueryRes,
    ExchangePair
)


# noinspection DuplicatedCode
class StockMarketInstrumentAV(StockMarketInstrument):   # may contain a stock, bond, or other instrument data
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


class SearchQueryResAV(SearchQueryRes):
    symbol: str                         = Field(alias="1. symbol")
    name: str                           = Field(alias="2. name")
    instrument_type: str                = Field(alias="3. type")
    region: Optional[str]               = Field(alias="4. region")
    market_open: str                    = Field(alias="5. marketOpen")
    market_close: str                   = Field(alias="6. marketClose")
    timezone: str                       = Field(alias="7. timezone")
    currency: Optional[str]             = Field(alias="8. currency")

    def to_markdown(self) -> str:
        md_str_end = \
            f"\n• ⏰ Open from __{self.market_open}__ to __{self.market_close}__" \
            f"\n• Timezone: {self.timezone}"
        return super().to_markdown() + md_str_end


class ExchangePairAV(ExchangePair):
    code_from: str                      = Field(alias="1. From_Currency Code")
    name_from: Optional[str]            = Field(alias="2. From_Currency Name")
    code_to: str                        = Field(alias="3. To_Currency Code")
    name_to: Optional[str]              = Field(alias="4. To_Currency Name")
    rate: float                         = Field(alias="5. Exchange Rate")
    last_refreshed: dt.datetime         = Field(alias="6. Last Refreshed")
    timezone: str                       = Field(alias="7. Time Zone")
    price_bid: Optional[float | None]   = Field(alias="8. Bid Price")
    price_ask: Optional[float | None]   = Field(alias="9. Ask Price")

    @field_validator('price_bid', mode="before")
    def validate_price_bid(cls, value):
        if value == "-":
            return None
        return value

    @field_validator('price_ask', mode="before")
    def validate_price_ask(cls, value):
        if value == "-":
            return None
        return value
