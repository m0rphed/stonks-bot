import datetime
from enum import unique, StrEnum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


@unique
class InstrumentType(StrEnum):
    sm_instrument = "stock_market_instrument"
    curr_pair = "currency_exchange_pair"
    crypto_pair = "crypto_exchange_pair"


class UserEntity(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime.datetime
    tg_user_id: int
    settings: dict | None


class InstrumentEntity(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    updated_at: datetime.datetime
    symbol: str
    figi_code: str | None
    price: float | None
    exchange_rate: float | None
    data_provider_code: str
    type: InstrumentType


class TrackingEntity(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime.datetime
    instrument: UUID = Field(default_factory=uuid4)
    tracked_by: UUID = Field(default_factory=uuid4)
    on_price: float | None
    on_rate: float | None
    notify_daily_at: Optional[datetime.datetime]


def create_tracking_obj(
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
