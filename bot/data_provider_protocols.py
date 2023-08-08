from abc import abstractmethod
from enum import unique, StrEnum
from typing import Protocol, runtime_checkable

from models import ExchangePair, StockMarketInstrument, SearchQueryRes


@unique
class ProviderT(StrEnum):
    STOCK_MARKET = "sm"
    CURR_FOREX = "frx"
    CURR_CRYPTO = "crp"
    UNIVERSAL = "uni"

    @property
    def description(self) -> str:
        match self.value:
            case "uni":
                return "universal data provider: stocks, forex, crypto"
            case "sm":
                return "stock market data provider: stocks, bonds, etc"
            case "frx":
                return "foreign fiat currency data provider: exchange rates"
            case "crp":
                return "crypto currency data provider: crypto exchange rates"


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
#   - IProviderStockMarket
#   - IProviderCurrEx
#   - IProviderCryptoEx


@runtime_checkable
class IProviderStockMarket(IDataProvider, Protocol):
    @abstractmethod
    def search_stock_market(self, query: str) -> list[SearchQueryRes]:
        ...

    @abstractmethod
    def get_security_by_ticker(self, ticker: str) -> StockMarketInstrument:
        ...


@runtime_checkable
class IProviderCurrEx(IDataProvider, Protocol):
    @abstractmethod
    def get_curr_pair(self, symbol_from: str, symbol_to: str) -> ExchangePair:
        ...


@runtime_checkable
class IProviderCryptoEx(IDataProvider, Protocol):
    @abstractmethod
    def get_crypto_pair(self, symbol_from: str, symbol_to: str) -> ExchangePair:
        ...


# Async protocols:
#   - IAsyncProviderStockMarket -- async methods for getting stock market prices
#   - IAsyncProviderCurrEx      -- async methods for getting currency exchange rates
#   - IAsyncProviderCryptoEx    -- async methods for getting cryptocurrency exchange rates


@runtime_checkable
class IAsyncProviderStockMarket(IDataProvider, Protocol):
    @abstractmethod
    async def search_stock_market(self, query: str) -> list[SearchQueryRes]:
        ...

    @abstractmethod
    async def get_security_by_ticker(self, ticker: str) -> StockMarketInstrument:
        ...


@runtime_checkable
class IAsyncProviderCurrEx(IDataProvider, Protocol):
    @abstractmethod
    async def get_curr_pair(self, symbol_from: str, symbol_to: str) -> ExchangePair:
        ...


@runtime_checkable
class IAsyncProviderCryptoEx(IDataProvider, Protocol):
    @abstractmethod
    async def get_crypto_pair(self, symbol_from: str, symbol_to: str) -> ExchangePair:
        ...
