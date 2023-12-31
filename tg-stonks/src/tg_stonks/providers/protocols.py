from abc import abstractmethod
from typing import Protocol, runtime_checkable

from tg_stonks.providers.provider_type import ProviderT
from tg_stonks.providers.models import (
    StockMarketInstrument,
    ExchangePair,
    SearchQueryRes
)


# Base protocol for data providers
@runtime_checkable
class IDataProvider(Protocol):
    @property
    @abstractmethod
    def provider_type(self) -> ProviderT:
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        ...


# Various types of data providers: use this to implement any kind of data providers
#   Such as: API, databases, any kind of libraries / packages
#   - IDataProviderStockMarket      -- async methods for getting stock market prices
#   - IDataProviderCurrencyEx       -- async methods for getting currency exchange rates
#   - IDataProviderCryptoEx         -- async methods for getting cryptocurrency exchange rates


@runtime_checkable
class IDataProviderStockMarket(IDataProvider, Protocol):
    @abstractmethod
    async def search_stock_market(self, query: str) -> list[SearchQueryRes]:
        ...

    @abstractmethod
    async def get_security_by_ticker(self, ticker: str) -> StockMarketInstrument:
        ...


@runtime_checkable
class IDataProviderCurrencyEx(IDataProvider, Protocol):
    @abstractmethod
    async def get_curr_pair(self, symbol_from: str, symbol_to: str) -> ExchangePair:
        ...


@runtime_checkable
class IDataProviderCryptoEx(IDataProvider, Protocol):
    @abstractmethod
    async def get_crypto_pair(self, symbol_from: str, symbol_to: str) -> ExchangePair:
        ...
