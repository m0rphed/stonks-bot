from abc import abstractmethod
from typing import Protocol, runtime_checkable

from returns.result import Result

from models import UserEntity, InstrumentEntity, TrackingEntity


class IDatabaseError(Exception):
    pass


@runtime_checkable
class IDatabase(Protocol):
    @abstractmethod
    def find_user_by_tg_id(self, tg_user_id: int) -> Result[UserEntity, any]:
        ...

    @abstractmethod
    def get_settings_of_user(self, tg_user_id: int) -> Result[dict, any]:
        ...

    @abstractmethod
    def find_curr_pair(self, code_from: str, code_to: str, data_provider: str) -> Result[InstrumentEntity, any]:
        ...

    @abstractmethod
    def find_crypto_pair(self, code_from: str, code_to: str, data_provider: str) -> Result[InstrumentEntity, any]:
        ...

    @abstractmethod
    def find_stock_market_instrument(self, ticker: str, data_provider: str) -> Result[InstrumentEntity, any]:
        ...

    @abstractmethod
    def find_instrument_by_fields(self, fields: dict) -> Result[InstrumentEntity, any]:
        ...

    @abstractmethod
    def find_tracking(self) -> Result[TrackingEntity, any]:
        ...

    @abstractmethod
    def find_tracking_by_fields(self) -> Result[TrackingEntity, any]:
        ...

    @abstractmethod
    def add_user_by_tg_id(self, tg_user_id: int):
        ...

    @abstractmethod
    def add_curr_pair(self):
        ...

    @abstractmethod
    def add_crypto_pair(self):
        ...

    @abstractmethod
    def add_instrument(self, instrument_fields: dict):
        ...

    @abstractmethod
    def add_tracking(self, tracking_fields: dict):
        ...

    @abstractmethod
    def delete_user_by_tg_id(self, tg_user_id: int):
        ...

    @abstractmethod
    def delete_instrument(self):
        ...

    @abstractmethod
    def delete_tracking(self):
        ...

    @abstractmethod
    def update_user(self, user_id: int, fields: dict):
        ...

    @abstractmethod
    def update_instrument(self):
        ...
