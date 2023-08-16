from enum import unique, StrEnum


@unique
class ProviderT(StrEnum):
    STOCK_MARKET = "sm"
    CURR_FOREX = "frx"
    CURR_CRYPTO = "crp"
    UNIVERSAL = "uni"

    @property
    def description(self) -> str:
        match self.value:
            case "uni":
                return "universal data provider: stocks, forex, crypto"
            case "sm":
                return "stock market data provider: stocks, bonds, etc"
            case "frx":
                return "foreign currency data provider: exchange rates"
            case "crp":
                return "crypto currency data provider: crypto exchange rates"

    @property
    def short(self) -> str:
        match self.value:
            case "uni":
                return "universal"
            case "sm":
                return "stock market only"
            case "frx":
                return "foreign currencies only"
            case "crp":
                return "cryptocurrencies only"
