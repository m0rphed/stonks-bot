from typing import final

from alpha_vantage.async_support.cryptocurrencies import CryptoCurrencies as CryptoCurrenciesAsync
from alpha_vantage.async_support.foreignexchange import ForeignExchange as ForeignExchangeAsync
from alpha_vantage.async_support.timeseries import TimeSeries as TimeSeriesAsync

from api_client_middleware import ApiClientMiddleware
from data_provider import AsyncProviderStockMarket, AsyncProviderCurrEx, AsyncProviderCryptoEx
from models_alpha_vantage import StockMarketInstrumentAV, SearchQueryResAV, ExchangePairAV


@final
class ClientTimeSeries(ApiClientMiddleware):
    def __init__(self, key: str):
        self.inner_client = TimeSeriesAsync(key)


@final
class ClientForEx(ApiClientMiddleware):
    def __init__(self, key: str):
        self.inner_client = ForeignExchangeAsync(key)


@final
class ClientCryptoEx(ApiClientMiddleware):
    def __init__(self, key: str):
        self.inner_client = CryptoCurrenciesAsync(key)


@final
class ApiAlphaVantage(AsyncProviderStockMarket, AsyncProviderCurrEx, AsyncProviderCryptoEx):
    data_provider_name: str = "alpha_vantage"

    def __init__(self, key: str):
        self._api_key = key

    async def search_stock_market(self, query: str) -> list[SearchQueryResAV]:
        async with ClientTimeSeries(self._api_key) as ts:
            # run search query and retrieve matching instruments
            search_results, _ = await ts.client.get_symbol_search(keywords=query)
            # add data provider field
            for res_dict in search_results:
                res_dict["data_provider"] = self.data_provider_name

            return [SearchQueryResAV.parse_obj(sr) for sr in search_results]

    async def get_security_by_ticker(self, ticker: str) -> StockMarketInstrumentAV:
        # init alpha-vantage client for stock market data
        async with ClientTimeSeries(self._api_key) as ts:
            # retrieve stock data by specified ticker symbol
            resp, _ = await ts.client.get_quote_endpoint(symbol=ticker)
            resp["data_provider"] = self.data_provider_name
            instrument = StockMarketInstrumentAV.parse_obj(resp)
            return instrument

    async def get_curr_pair(self, symbol_from: str, symbol_to: str) -> ExchangePairAV:
        # init alpha-vantage client for foreign exchange data
        async with ClientForEx(self._api_key) as fx:
            # retrieve foreign exchange data by specified currency codes/symbols
            resp, _ = await fx.client.get_currency_exchange_rate(
                from_currency=symbol_from,
                to_currency=symbol_to
            )
            resp["data_provider"] = self.data_provider_name
            instrument = ExchangePairAV.parse_obj(resp)
            return instrument

    async def get_crypto_pair(self, symbol_from: str, symbol_to: str) -> ExchangePairAV:
        async with ClientCryptoEx(self._api_key) as cc:
            resp, _ = await cc.client.get_digital_currency_exchange_rate(
                from_currency=symbol_from,
                to_currency=symbol_to
            )
            resp["data_provider"] = self.data_provider_name
            instrument = ExchangePairAV.parse_obj(resp)
            return instrument