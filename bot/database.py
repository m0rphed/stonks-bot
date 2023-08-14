from abc import abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class IDatabase(Protocol):
    @abstractmethod
    def user_with(self, fields: dict) -> list[dict]:
        """Get user from 'bot_users' table with matching fields;
        """
        ...

    @abstractmethod
    def user_with_tg_id(self, tg_user_id: int) -> dict:
        """Get user from 'bot_users' table with matching 'tg_user_id' field;
        Expected exactly one user
        """
        ...

    @abstractmethod
    def settings_of_tg_id(self, tg_user_id: int) -> dict:
        """Get settings (JSON object) of the user with matching 'tg_user_id' field;
        Expected exactly one user = exactly one user settings JSON
        """
        ...

    @abstractmethod
    def find_curr_pair(self, code_from: str, code_to: str, data_provider: str) -> dict:
        ...

    @abstractmethod
    def find_crypto_pair(self, code_from: str, code_to: str, data_provider: str) -> dict:
        ...

    @abstractmethod
    def find_stock_market_instrument(self, symbol: str, data_provider: str) -> dict:
        ...

    @abstractmethod
    def find_instrument_with(self, fields: dict) -> dict:
        ...

    @abstractmethod
    def find_tracking_with(self, fields: dict) -> dict:
        ...

    @abstractmethod
    def trackings_with(self, fields: dict) -> list[dict]:
        ...

    @abstractmethod
    def add_new_user(self, tg_user_id: int):
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
