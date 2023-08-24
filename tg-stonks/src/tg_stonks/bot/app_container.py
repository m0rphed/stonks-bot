from dataclasses import dataclass

from tg_stonks.providers.helpers import filter_by_name, filter_by_protocol_impl
from tg_stonks.providers.protocols import IDataProvider, IDataProviderStockMarket
from tg_stonks.database.protocols import IDatabase


@dataclass(frozen=True)
class AppContainer:
    database: IDatabase
    data_providers: list[IDataProvider]

    def get_provider_by_name(self, name: str):
        return filter_by_name(self.data_providers, name)

    def provider_stock_market_by_name(self, prov_name: str) -> IDataProviderStockMarket:
        for prov in self.providers_stock_market():
            if prov.provider_name == prov_name:
                return prov

        raise Exception(f"No providers with '{prov_name}' name found")

    def providers_stock_market(self) -> list[IDataProviderStockMarket]:
        return filter_by_protocol_impl(self.data_providers, IDataProviderStockMarket)
