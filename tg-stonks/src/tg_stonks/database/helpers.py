import asyncio
from typing import Callable, Any

from returns.result import Success, Result, safe

from tg_stonks.database.entity_models import (
    UserEntity,
    InstrumentEntity,
    TrackingEntity
)
from tg_stonks.database.protocols import IDatabase
from tg_stonks.database.user_settings import DataProviderConfig, UserSettings


def to_user(user_obj: dict) -> UserEntity:
    return UserEntity.model_validate(
        user_obj,
        strict=True
    )


def to_instrument(instrument_obj: dict) -> InstrumentEntity:
    return InstrumentEntity.model_validate(
        instrument_obj,
        strict=True
    )


def to_tracking(tracking_obj: dict) -> TrackingEntity:
    return TrackingEntity.model_validate(
        tracking_obj,
        strict=True
    )


def res_to_user(res: Result[dict, Any]) -> Result:
    if isinstance(res, Success):
        parsed_user = UserEntity.model_validate(
            res.unwrap(),
            strict=True
        )
        return Success(parsed_user)
    return res


def res_to_instrument(res: Result[dict, Any]) -> Result:
    if isinstance(res, Success):
        parsed_instrument = InstrumentEntity.model_validate(
            res.unwrap(),
            strict=True
        )
        return Success(parsed_instrument)
    return res


def res_to_tracking(res: Result[dict, Any]) -> Result:
    if isinstance(res, Success):
        parsed_tracking = TrackingEntity.model_validate(
            res.unwrap(),
            strict=True
        )
        return Success(parsed_tracking)
    return res


@safe
def try_get_user_by_id(db: IDatabase, tg_user_id: int):
    return db.user_with_tg_id(tg_user_id)


@safe
def try_get_settings_of_user(db: IDatabase, tg_user_id: int):
    settings: dict = db.settings_of_tg_user_id(tg_user_id)

    # 'settings' column could be NULL
    # - so, this should prevent validation error
    if settings is None:
        return UserSettings.model_validate({
            "provider_stock_market": None,
            "provider_currency": None,
            "provider_crypto": None
        }, strict=True)

    return UserSettings.model_validate(
        settings,
        strict=True
    )


@safe
def try_get_provider(db: IDatabase, tg_user_id: int, provider_t: str):
    settings: dict = db.settings_of_tg_user_id(tg_user_id)
    prov_conf_obj = settings.get(provider_t)
    if prov_conf_obj is not None:
        return DataProviderConfig.model_validate(
            prov_conf_obj,
            strict=True
        )

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
