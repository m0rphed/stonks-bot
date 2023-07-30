from typing import Optional

from pydantic import BaseModel


class User:  # abstract user
    pass


class UserPreferences:  # contains token information
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
    pass


class InstrumentEntity:
    pass


class ExchangePairEntity:
    pass


class TrackingEntity:
    pass
