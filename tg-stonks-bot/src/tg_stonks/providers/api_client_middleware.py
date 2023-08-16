from abc import ABC, abstractmethod

from loguru import logger


class ApiClientMiddleware(ABC):
    @abstractmethod
    def __init__(self, _key: str):
        self._client = None
        raise NotImplementedError("Expected to implement `__init__` in child class")

    async def __aenter__(self):
        self._safely_initialized = True
        return self

    async def __aexit__(self, *args, **kwargs):
        await self._client.close()
        logger.info(f"API client exited ({self.__class__.__name__})")

    def _fail_on_unsafe_init(self) -> None:
        if not self.initialized_safely:
            raise RuntimeError(
                "You should only use this class via:"
                f" `async with {self.__class__.__name__}(...) as <alias name>: ...`")

    @property
    def client(self):
        self._fail_on_unsafe_init()
        return self._client

    @property
    def initialized_safely(self) -> bool:
        return self._safely_initialized
