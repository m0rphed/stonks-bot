from typing import Optional

from pydantic import BaseModel, field_validator

from tg_stonks.providers.provider_type import ProviderT


class DataProviderConfig(BaseModel):
    name: str
    type: ProviderT
    user_credentials: bool = False
    own_credentials: Optional[dict] = None

    @field_validator("own_credentials", mode="before")
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

    @field_validator("other_settings", mode="before")
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
