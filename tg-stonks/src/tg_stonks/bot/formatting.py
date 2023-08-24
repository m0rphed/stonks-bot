import emoji

from tg_stonks.providers.protocols import IDataProvider
import datetime as dt


def msg_warning(msg: str) -> str:
    return "⚠️ " + msg


def msg_error(msg: str) -> str:
    return "⛔ " + msg


def msg_ok(msg: str) -> str:
    return "✅ " + msg


def _region_emoji_or_empty(reg_str: str) -> str:
    supported_regions = {"Frankfurt": ":flag_for_Germany:",
                         "XETRA": ":flag_for_Germany:",
                         "United States": ":flag_for_United_States:",
                         "United Kingdom": ":flag_for_United_Kingdom:",
                         "Brazil/Sao Paolo": ":flag_for_Brazil:"}

    if reg_str not in supported_regions.keys():
        return ""

    return emoji.emojize(supported_regions[reg_str], language="alias")


def stock_confirmation(ticker: str, price: str | int | float, exchange: str, data_provider: str) -> str:
    reply_message = f"Stock information:\n\n" \
                    f"Ticket: {ticker}\n" \
                    f"Price: {price}\n" \
                    f"Exchange: {exchange}\n" \
                    f"• provided by 👉 `{data_provider}`\n" \
                    f"\nIf this is the correct stock you want to track, click the button below to confirm."

    return reply_message


def curr_pair_confirmation(
        code_from: str,
        code_to: str,
        price: str | int | float,
        rate: str | int | float,
        exchange: str,
        data_provider: str) -> str:
    reply_message = f"Currency exchange pair information:\n\n" \
                    f"From `{code_from}` to `{code_to}`\n" \
                    f"Price: {price}\n" \
                    f"Exchange rate: {rate}\n" \
                    f"Exchange: {exchange}\n" \
                    f"• provided by 👉 `{data_provider}`\n" \
                    f"\nIf this is the correct exchange pair you want to track," \
                    " click the button below to confirm."

    return reply_message


def msg_list_providers(providers: list[IDataProvider]) -> str:
    msg = "Available data providers:\n"
    for available_prov in providers:
        name = available_prov.provider_name
        prov_type = available_prov.provider_type
        msg += f"\n• `{name}` 👉 {prov_type.description}"
    return msg


def msg_instrument_updated(instrument_obj: dict, tracking_obj: dict) -> str:
    res_str = "⚡️**Instrument updated**⚡️\n"
    res_str += f"\n• 👉 --Ticker / symbol--: `{instrument_obj['symbol']}`\n"
    res_str += f"\n• 🕓 Updated at: *{instrument_obj['updated_at']}*"

    if tracking_obj.get("on_price") is not None:
        res_str += f"\n• 🔔 Notify on price: `{tracking_obj['on_price']}`"

    if tracking_obj.get("on_rate") is not None:
        res_str += f"\n• 🔔 Notify on rate: `{tracking_obj['on_rate']}`"

    if instrument_obj.get("price") is not None:
        res_str += f"\n• 💸 Current price `{instrument_obj['price']}`"

    if instrument_obj.get("exchange_rate") is not None:
        res_str += f"\n• 💱 Current exchange rate: `{instrument_obj['exchange_rate']}`"

    if instrument_obj.get("figi_code") is not None:
        res_str += f"\n• 🔑 The FIGI Code is: `{instrument_obj['figi_code']}`"

    # last_upd_at = dt.datetime.fromisoformat(instrument_obj["updated_at"])
    res_str += f"\n• 🔮 Data from: `{instrument_obj['data_provider_code']}`"
    return res_str
