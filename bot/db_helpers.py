from returns.result import Success, Result

from models import UserEntity, InstrumentEntity, TrackingEntity


def _to_user_entity(res: Result[dict, any]) -> Result:
    if isinstance(res, Success):
        parsed_user = UserEntity.parse_obj(res.unwrap())
        return Success(parsed_user)
    return res


def _to_instrument(res: Result[dict, any]) -> Result:
    if isinstance(res, Success):
        parsed_instrument = InstrumentEntity.parse_obj(res.unwrap())
        return Success(parsed_instrument)
    return res


def _to_tracking(res: Result[dict, any]) -> Result:
    if isinstance(res, Success):
        parsed_tracking = TrackingEntity.parse_obj(res.unwrap())
        return Success(parsed_tracking)
    return res
