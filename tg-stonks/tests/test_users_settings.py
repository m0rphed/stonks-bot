import pprint
from tg_stonks.bot.helpers import make_prov_settings
from tg_stonks.database.user_settings import DataProviderConfig

from tg_stonks.providers.provider_type import ProviderT


def test_make_provider_dict_by_type():
    settings = make_prov_settings(
        ProviderT.UNIVERSAL,
        DataProviderConfig.model_validate({
            "name": "alpha-vantage",
            "type": "uni",
            "user_credentials": False
        }))

    print("\n")
    pprint.pprint(settings)

    assert settings["provider_stock_market"]["name"] == "alpha-vantage"
    assert settings["provider_currency"]["name"] == "alpha-vantage"
    assert settings["provider_crypto"]["name"] == "alpha-vantage"
