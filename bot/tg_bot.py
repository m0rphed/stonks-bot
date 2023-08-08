import asyncio
from dataclasses import dataclass

from pyrogram import Client

from data_provider import by_name, filter_by_class
from data_provider_protocols import (
    IDataProvider,
    IProviderStockMarket,
    IProviderCurrEx,
    IProviderCryptoEx,
    IAsyncProviderStockMarket,
    IAsyncProviderCurrEx,
    IAsyncProviderCryptoEx
)
from db import IDatabase


@dataclass(frozen=True)
class TelegramCreds:
    api_id: int
    api_hash: str
    bot_token: str


class TgBot:
    def __init__(
            self,
            session_name: str,
            tg_creds: TelegramCreds,
            db_prov: IDatabase,
            data_providers: list[IDataProvider]
    ):
        TgBot.__check_protocols(db_prov, data_providers)
        self._database = db_prov
        self._providers = data_providers
        self._tg = tg_creds
        self._pyro_app = Client(
            name=session_name, api_id=self._tg.api_id,
            api_hash=self._tg.api_hash,
            bot_token=self._tg.bot_token
        )

    @staticmethod
    def __check_protocols(db, providers: list[IDataProvider]):
        if not isinstance(db, IDatabase):
            raise ValueError(f"{db} should impl. protocol `IDatabase`")

        for prov in providers:
            if not isinstance(prov, IDataProvider):
                raise ValueError(f"{prov} should impl. protocol `IDataProvider`")

    @property
    def db(self) -> IDatabase:
        return self._database

    @property
    def data_providers(self) -> list[IDataProvider]:
        return self._providers

    @property
    def app(self) -> Client:
        return self._pyro_app

    def get_provider_by_name(self, name: str):
        return by_name(self.data_providers, name)

    def get_prov_stock_market(self, prov_name: str) -> IAsyncProviderStockMarket | IProviderStockMarket:
        for prov in self.get_providers_stock_market():
            if prov.provider_name == prov_name:
                return prov

        raise Exception(f"No providers with '{prov_name}' name found")

    def get_providers_stock_market(self) -> list[IAsyncProviderStockMarket | IProviderStockMarket]:
        async_xs: list = filter_by_class(self.data_providers, IAsyncProviderStockMarket)
        xs: list = filter_by_class(self.data_providers, IProviderStockMarket)
        return xs + async_xs

    def get_providers_curr_ex(self) -> list[IAsyncProviderCurrEx | IProviderCurrEx]:
        raise NotImplementedError

    def get_providers_crypto_ex(self) -> list[IAsyncProviderCryptoEx | IProviderCryptoEx]:
        raise NotImplementedError

    def run(self):
        asyncio.run(self._pyro_app.run())
