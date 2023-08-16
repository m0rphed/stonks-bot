from tg_stonks.providers.protocols import IDataProvider
from tg_stonks.providers.provider_type import ProviderT


def by_name(providers: list[IDataProvider], name: str) -> IDataProvider:
    for prov in providers:
        if prov.provider_name == name:
            return prov
        raise RuntimeError(f"No data providers with name {name}' found")


def filter_by_type(providers: list[IDataProvider], prov_type: ProviderT) -> list:
    res = [
        prov for prov in providers
        if prov.provider_type == prov_type
    ]

    return res


def filter_by_implementation(providers: list[IDataProvider], prov_class) -> list:
    filtered = []
    for prov in providers:
        if isinstance(prov, prov_class):
            filtered.append(prov)

    return filtered
