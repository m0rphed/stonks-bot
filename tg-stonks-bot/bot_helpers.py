from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from data_provider import IDataProvider
from data_provider_type import ProviderT
from formatting import msg_error
from user_settings import DataProviderConfig


def confirmation_markup(cb_data_confirmed: str, cb_data_canceled: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[
            InlineKeyboardButton(
                "✅ Confirm", callback_data=cb_data_confirmed
            ),
            InlineKeyboardButton(
                "❌ Cancel", callback_data=cb_data_canceled
            )
        ]]
    )


def cancel_btn(callback_data_suffix: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        "❌ Cancel",
        callback_data=f"canceled {callback_data_suffix}"
    )


def set_prov_btn(btn_text: str, prov_t: str, prov_name: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        btn_text,
        callback_data=f"confirmed --cmd prov {prov_t} {prov_name}"
    )


def chose_provider_markup(prov: IDataProvider) -> tuple[str, InlineKeyboardMarkup]:
    match prov.provider_type:
        case ProviderT.STOCK_MARKET:
            msg = "Set this provider for --stock market-- data 🚀📈🦬"
            markup = InlineKeyboardMarkup(
                [[
                    set_prov_btn("Set for stock market", ProviderT.STOCK_MARKET.value, prov.provider_name),
                    cancel_btn("--cmd prov")
                ]]
            )
            return msg, markup

        case ProviderT.CURR_FOREX:
            msg = "Set this provider for --foreign currency exchange-- data 💹💲💱"
            markup = InlineKeyboardMarkup(
                [[
                    set_prov_btn("Set for forex market", ProviderT.CURR_FOREX.value, prov.provider_name),
                    cancel_btn("--cmd prov")
                ]]
            )
            return msg, markup

        case ProviderT.CURR_CRYPTO:
            msg = "Set this provider for --cryptocurrency-- data ₿👩🏻‍💻🌐"
            markup = InlineKeyboardMarkup(
                [[
                    set_prov_btn("Set for crypto market", ProviderT.CURR_CRYPTO.value, prov.provider_name),
                    cancel_btn("--cmd prov")
                ]]
            )
            return msg, markup

        case ProviderT.UNIVERSAL:
            msg = "You can set this provider for --all kinds-- of data 📈💹₿"
            markup = InlineKeyboardMarkup(
                [
                    [set_prov_btn("Set for stock market", ProviderT.STOCK_MARKET.value, prov.provider_name)],
                    [set_prov_btn("Set for forex market", ProviderT.CURR_FOREX.value, prov.provider_name)],
                    [set_prov_btn("Set for crypto market", ProviderT.CURR_CRYPTO.value, prov.provider_name)],
                    [set_prov_btn("Set for everything", ProviderT.UNIVERSAL.value, prov.provider_name)],
                    [cancel_btn("--cmd prov")]
                ]
            )
            return msg, markup


async def _running_without_providers(message: Message):
    await message.reply(
        msg_error(
            "Bot running without any data providers passed"
        )
    )


def _providers_settings2(prov_t_value: str, prov_conf: DataProviderConfig) -> dict:
    match prov_t_value:
        case ProviderT.UNIVERSAL:
            return {
                "provider_stock_market": prov_conf.dict(),
                "provider_currency": prov_conf.dict(),
                "provider_crypto": prov_conf.dict()
            }
        case ProviderT.CURR_CRYPTO:
            return {
                "provider_stock_market": None,
                "provider_currency": None,
                "provider_crypto": prov_conf.dict()
            }

        case ProviderT.CURR_FOREX:
            return {
                "provider_stock_market": None,
                "provider_currency": prov_conf.dict(),
                "provider_crypto": None
            }

        case ProviderT.STOCK_MARKET:
            return {
                "provider_stock_market": prov_conf.dict(),
                "provider_currency": None,
                "provider_crypto": None
            }