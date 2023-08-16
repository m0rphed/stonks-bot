from dataclasses import dataclass

from tg_stonks.providers.helpers import by_name, filter_by_implementation
from tg_stonks.providers.protocols import IDataProvider, IDataProviderStockMarket
from tg_stonks.database.protocols import IDatabase


@dataclass(frozen=True)
class AppContainer:
    database: IDatabase
    data_providers: list[IDataProvider]

    def get_provider_by_name(self, name: str):
        return by_name(self.data_providers, name)

    def stock_market_provider_by_name(self, prov_name: str) -> IDataProviderStockMarket:
        for prov in self.stock_market_providers():
            if prov.provider_name == prov_name:
                return prov

        raise Exception(f"No providers with '{prov_name}' name found")

    def stock_market_providers(self) -> list[IDataProviderStockMarket]:
        return filter_by_implementation(self.data_providers, IDataProviderStockMarket)
