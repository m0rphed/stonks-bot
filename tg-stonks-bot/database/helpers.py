import asyncio
from typing import Callable, Any

from returns.result import Success, Result, safe

from models import UserEntity, InstrumentEntity, TrackingEntity
from user_settings import DataProviderConfig, UserSettings
from .protocol import IDatabase


def to_user(user_obj: dict) -> UserEntity:
    return UserEntity.parse_obj(
        user_obj
    )


def to_instrument(instrument_obj: dict) -> InstrumentEntity:
    return InstrumentEntity.parse_obj(
        instrument_obj
    )


def to_tracking(tracking_obj: dict) -> TrackingEntity:
    return TrackingEntity.parse_obj(
        tracking_obj
    )


def res_to_user(res: Result[dict, Any]) -> Result:
    if isinstance(res, Success):
        parsed_user = UserEntity.parse_obj(res.unwrap())
        return Success(parsed_user)
    return res


def res_to_instrument(res: Result[dict, Any]) -> Result:
    if isinstance(res, Success):
        parsed_instrument = InstrumentEntity.parse_obj(res.unwrap())
        return Success(parsed_instrument)
    return res


def res_to_tracking(res: Result[dict, Any]) -> Result:
    if isinstance(res, Success):
        parsed_tracking = TrackingEntity.parse_obj(res.unwrap())
        return Success(parsed_tracking)
    return res


@safe
def try_get_user_by_id(db: IDatabase, tg_user_id: int):
    return db.user_with_tg_id(tg_user_id)


@safe
def try_get_settings_of_user(db: IDatabase, tg_user_id: int):
    settings: dict = db.settings_of_tg_id(tg_user_id)

    # 'settings' column could be NULL
    # - so, this should prevent validation error
    if settings is None:
        return UserSettings.parse_obj({
            "provider_stock_market": None,
            "provider_currency": None,
            "provider_crypto": None
        })

    return UserSettings.parse_obj(settings)


@safe
def try_get_provider(db: IDatabase, tg_user_id: int, provider_t: str):
    settings: dict = db.settings_of_tg_id(tg_user_id)
    prov_conf_obj = settings.get(provider_t)
    if prov_conf_obj is not None:
        return DataProviderConfig.parse_obj(prov_conf_obj)

    raise Exception("provider not set")


# TODO: this function should be in another module
def ensure_awaited(
        func: Callable,
        *func_args,
        **func_kwargs) -> Any:
    if asyncio.iscoroutinefunction(func):
        loop = func_kwargs.get("loop") if func_kwargs.get("loop") is not None else asyncio.get_event_loop()
        return loop.run_until_complete(func(*func_args, **func_kwargs))
    else:
        return func(*func_args, **func_kwargs)
