from typing import Optional

from pydantic import BaseModel, validator

from ..data_providers.provider_type import ProviderT


class DataProviderConfig(BaseModel):
    name: str
    type: ProviderT
    user_credentials: bool = False
    own_credentials: Optional[dict] = None

    @validator("own_credentials", pre=True)
    def prevent_none(cls, value):
        assert value is not None, \
            "'own_credentials' shouldn't be" \
            " set to 'None', simply omit this field"
        return value

    def to_markdown(self):
        _name = self.name + ".personal" if self.user_credentials else self.name
        return f"`{_name}` ({self.type.short})"


class UserSettings(BaseModel):
    provider_stock_market: Optional[DataProviderConfig] = None
    provider_currency: Optional[DataProviderConfig] = None
    provider_crypto: Optional[DataProviderConfig] = None
    other_settings: Optional[dict] = None

    @validator("other_settings", pre=True)
    def prevent_none(cls, value):
        assert value is not None, \
            "'other_settings' shouldn't be" \
            " set to 'None', simply omit this field"
        return value

    def is_all_providers_null(self):
        return (
            self.provider_stock_market is None
            and self.provider_currency is None
            and self.provider_crypto is None
        )

    def to_markdown(self) -> str:
        ns = "⚠️ not set"
        msg_beg = "🔧 Settings:"
        msg_end = (
            "\n➜ Other settings: "
            + ns if self.other_settings is None else str(self.other_settings)
        )
        if self.is_all_providers_null():
            return msg_beg + "\n➜ Providers: ⚠️ *providers not set*" + msg_end

        sm, curr, cryp = (
            self.provider_stock_market,
            self.provider_currency,
            self.provider_crypto
        )

        prov_sm = ns if sm is None else sm.to_markdown()
        prov_curr = ns if curr is None else curr.to_markdown()
        prov_cryp = ns if cryp is None else cryp.to_markdown()

        return (
            msg_beg +
            "\n➜ Providers:"
            f"\n• of stock market data: {prov_sm}"
            f"\n• of foreign currencies data: {prov_curr}"
            f"\n• of cryptocurrencies data: {prov_cryp}"
            + msg_end
        )


if __name__ == "__main__":
    prov_config = {
        "name": "alpha-vantage",
        "type": "uni",
        "user_credentials": True,
        "own_credentials": {"key": "123"}
    }
    x = DataProviderConfig.parse_obj(prov_config)
    print(x)
    print(
        x.type,
        type(x.type),
        ProviderT.UNIVERSAL == x.type
    )

    y = DataProviderConfig.parse_obj({
        "name": "alpha-vantage",
        "type": "uni",
        "user_credentials": False
    })
    print(y)

    yy = UserSettings.parse_obj(
        # {
        #     "provider_stock_market": None,
        #     "provider_currency": None,
        #     "provider_crypto": None
        # }
        {
            "provider_stock_market": {
                "name": "alpha-vantage",
                "type": "uni",
                "user_credentials": False
            },
            # "provider_currency": {
            #     "name": "alpha-vantage",
            #     "type": "uni",
            #     "user_credentials": False
            # },
            "provider_crypto": {
                "name": "alpha-vantage",
                "type": "uni",
                "user_credentials": False
            }
        }

    )

    print(yy.to_markdown())
