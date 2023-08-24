import datetime
from enum import unique, StrEnum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field
from pydantic.types import UUID4


@unique
class InstrumentType(StrEnum):
    """
    Enum defines different types of financial instruments:
    - 'stock_market_instrument' is for anything related to stock market e.g.
        any securities like: equities (stocks, shares), bonds etc.
    - 'currency_exchange_pair' is for foreign currency to crypto/another foreign currency exchange rates & prices e.g.
        - GBP (foreign curr.) => RUB (another foreign curr.),
        - CNY (foreign curr.) => BTC (crypto curr.),
        - [!] but not: BTC (cryptocurrency) => ETH (another cryptocurrency)
    - 'crypto_exchange_pair' is for cryptocurrency-to-cryptocurrency exchange rates & prices e.g.
        - BTC (Bitcoin is cryptocurrency) => ETH (Ethereum is another cryptocurrency),
        - ETH (Ethereum) => XMR (Monero),
        - XMR (Monero) => ETH (Ethereum) - reverse order conversion is treated
        as different pair (because rates and prices may vary)
    """
    sm_instrument = "stock_market_instrument"
    curr_pair = "currency_exchange_pair"
    crypto_pair = "crypto_exchange_pair"


class UserEntity(BaseModel):
    """
    Represents a bot user

    - 'id' is an inner DB table identifier (expected to be unique in the table) [NOT NULL];
    - 'created_at' is a timestamp (with timezone information) which indicates
    at what time this user was added to DB (could be automatically assigned at user creation) [NOT NULL];
    - 'tg_user_id' is a telegram id of this user which uses the bot (unique for each user in telegram) [NOT NULL];
    - 'settings' is a JSON field which stores user's settings [NULLABLE]
    """
    id: UUID4 = Field(default_factory=uuid4)
    created_at: datetime.datetime
    tg_user_id: int
    settings: dict | None


class InstrumentEntity(BaseModel):
    """
    Represents a financial instrument, be it a stock, a currency pair, or a cryptocurrency pair
    """
    id: UUID4 = Field(default_factory=uuid4)
    updated_at: datetime.datetime
    symbol: str
    figi_code: str | None
    price: float | None
    exchange_rate: float | None
    data_provider_code: str
    type: InstrumentType


class TrackingEntity(BaseModel):
    """
    Represents a tracking order of existing financial instrument created by bot user
    """
    id: UUID4 = Field(default_factory=uuid4)
    created_at: datetime.datetime
    instrument: UUID4 = Field(default_factory=uuid4)
    tracked_by: UUID4 = Field(default_factory=uuid4)
    on_price: float | None
    on_rate: float | None
    notify_daily_at: Optional[datetime.datetime]


def make_tracking_obj_of_instrument(
        user: UserEntity,
        instrument: InstrumentEntity,
        on_price: float | None = None,
        on_rate: float | None = None,
        notify_daily_at: datetime.datetime | None = None) -> dict:
    # set everything except "id", and "created_at" field
    return {
        "instrument": str(instrument.id),
        "tracked_by": str(user.id),
        "on_price": on_price,
        "on_rate": on_rate,
        "notify_daily_at": notify_daily_at
    }
