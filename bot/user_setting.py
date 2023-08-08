from typing import TypedDict, Optional

from data_provider_protocols import ProviderT


class ProviderSettings(TypedDict):
    is_key_required: bool
    prov_name: str
    prov_type: ProviderT
    token_or_key: Optional[str]


class UserSettings(TypedDict):  # contains data provider information
    providers: list[ProviderSettings]
    default_stock_provider: Optional[str]
    default_forex_provider: Optional[str]
    default_crypto_provider: Optional[str]
