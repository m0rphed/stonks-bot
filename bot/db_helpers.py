from returns.result import Success, Result

from models import UserEntity, InstrumentEntity, TrackingEntity


def to_user(user_obj: dict) -> UserEntity:
    return UserEntity.parse_obj(
        user_obj
    )


def res_to_user(res: Result[dict, any]) -> Result:
    if isinstance(res, Success):
        parsed_user = UserEntity.parse_obj(res.unwrap())
        return Success(parsed_user)
    return res


def to_instrument(instrument_obj: dict) -> InstrumentEntity:
    return InstrumentEntity.parse_obj(
        instrument_obj
    )


def res_to_instrument(res: Result[dict, any]) -> Result:
    if isinstance(res, Success):
        parsed_instrument = InstrumentEntity.parse_obj(res.unwrap())
        return Success(parsed_instrument)
    return res


def to_tracking(tracking_obj: dict) -> TrackingEntity:
    return TrackingEntity.parse_obj(
        tracking_obj
    )


def res_to_tracking(res: Result[dict, any]) -> Result:
    if isinstance(res, Success):
        parsed_tracking = TrackingEntity.parse_obj(res.unwrap())
        return Success(parsed_tracking)
    return res
