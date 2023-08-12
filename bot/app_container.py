from dataclasses import dataclass

from data_provider import by_name, filter_by_class
from data_provider_protocols import (
    IDataProvider,
    IProviderStockMarket,
    IAsyncProviderStockMarket
)
from db import IDatabase


@dataclass(frozen=True)
class AppContainer:
    db: IDatabase
    data_providers: list[IDataProvider]

    def get_provider_by_name(self, name: str):
        return by_name(self.data_providers, name)

    def get_prov_stock_market(self, prov_name: str) -> IAsyncProviderStockMarket | IProviderStockMarket:
        for prov in self.get_providers_stock_market():
            if prov.provider_name == prov_name:
                return prov

        raise Exception(f"No providers with '{prov_name}' name found")

    def get_providers_stock_market(self) -> list[IAsyncProviderStockMarket | IProviderStockMarket]:
        async_xs = filter_by_class(self.data_providers, IAsyncProviderStockMarket)
        xs = filter_by_class(self.data_providers, IProviderStockMarket)
        return xs + async_xs  # TODO: why we combine different kind of APIs together? (stop it, get some help)
