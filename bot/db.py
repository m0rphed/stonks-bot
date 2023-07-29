from abc import abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class DatabaseProvider(Protocol):
    @abstractmethod
    def check_user(self, tg_user_id):
        ...

    @abstractmethod
    def check_curr_pair(self, code_from: str, code_to: str, data_provider: str):
        ...

    @abstractmethod
    def check_crypto_pair(self, code_from: str, code_to: str, data_provider: str):
        ...

    @abstractmethod
    def check_instrument(self, ticker: str, data_provider: str):
        ...

    @abstractmethod
    def check_instrument_by_fields(self):
        ...

    @abstractmethod
    def check_tracking(self):
        ...

    @abstractmethod
    def check_tracking_by_fields(self):
        ...

    @abstractmethod
    def add_user_by_id(self, tg_user_id: int):
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
    def delete_user(self):
        ...

    @abstractmethod
    def delete_instrument(self):
        ...

    @abstractmethod
    def delete_tracking(self):
        ...

    @abstractmethod
    def update_user(self):
        ...

    @abstractmethod
    def update_instrument(self):
        ...
