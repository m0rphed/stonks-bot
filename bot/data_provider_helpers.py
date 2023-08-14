from data_provider import IDataProvider
from data_provider_type import ProviderT


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


def filter_by_class(providers: list[IDataProvider], prov_class) -> list:
    filtered = []
    for prov in providers:
        if isinstance(prov, prov_class):
            filtered.append(prov)

    return filtered


if __name__ == "__main__":
    from provider_alpha_vantage import AlphaVantageAPI

    xs = [
        AlphaVantageAPI("fake_key_01"),
        AlphaVantageAPI("fake_key_02"),
        AlphaVantageAPI("fake_key_03"),
        AlphaVantageAPI("fake_key_04")
    ]

    flt = filter_by_type(xs, ProviderT.UNIVERSAL)
    assert len(flt), len(xs)

    flt = filter_by_class([AlphaVantageAPI("fake_key")], IDataProvider)
    assert len(flt), 1

    print("all tests passed")
