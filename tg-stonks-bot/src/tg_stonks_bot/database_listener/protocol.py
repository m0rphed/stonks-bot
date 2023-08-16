from abc import abstractmethod
from typing import Callable, Protocol, runtime_checkable


@runtime_checkable
class IDatabaseListener(Protocol):
    @abstractmethod
    def add_callback(self, event_type: str, call_back_func: Callable):
        ...

    @abstractmethod
    def start_listening(self, **kwargs):
        ...
