from abc import abstractmethod
from typing import Protocol, runtime_checkable

from data_models import ExchangePair, StockMarketInstrument, SearchQueryRes


@runtime_checkable
class ProviderStockMarket(Protocol):
    @abstractmethod
    def search_stock_market(self, query: str) -> list[SearchQueryRes]:
        ...

    @abstractmethod
    def get_security_by_ticker(self, ticker: str) -> StockMarketInstrument:
        ...


@runtime_checkable
class AsyncProviderStockMarket(Protocol):
    @abstractmethod
    async def search_stock_market(self, query: str) -> list[SearchQueryRes]:
        ...

    @abstractmethod
    async def get_security_by_ticker(self, ticker: str) -> StockMarketInstrument:
        ...


# noinspection DuplicatedCode
@runtime_checkable
class ProviderCryptoEx(Protocol):
    @abstractmethod
    def get_crypto_pair(self, symbol_from: str, symbol_to: str) -> ExchangePair:
        ...


@runtime_checkable
class AsyncProviderCryptoEx(Protocol):
    @abstractmethod
    async def get_crypto_pair(self, symbol_from: str, symbol_to: str) -> ExchangePair:
        ...


# noinspection DuplicatedCode
@runtime_checkable
class ProviderCurrEx(Protocol):
    @abstractmethod
    def get_curr_pair(self, symbol_from: str, symbol_to: str) -> ExchangePair:
        ...


@runtime_checkable
class AsyncProviderCurrEx(Protocol):
    @abstractmethod
    async def get_curr_pair(self, symbol_from: str, symbol_to: str) -> ExchangePair:
        ...
