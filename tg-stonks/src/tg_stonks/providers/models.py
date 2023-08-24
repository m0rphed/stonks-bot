from typing import Optional

from pydantic import BaseModel


class StockMarketInstrument(BaseModel):
    """
    Represents stock market instrument model
    """
    symbol: str
    price: float
    data_provider: str
    exchange: Optional[str]


class ExchangePair(BaseModel):
    """
    Represents fiat or cryptocurrency exchange pair model
    """
    code_from: str
    code_to: str
    rate: float
    name_from: Optional[str]
    name_to: Optional[str]
    data_provider: str
    exchange: Optional[str]


class SearchQueryRes(BaseModel):
    """
    Represents result of a search query
    """
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
