from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from data_provider_protocols import ProviderT, IDataProvider
from formatting import msg_error


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


def _providers_settings(str_type_value: str, prov_name: str) -> dict:
    match str_type_value:
        case ProviderT.UNIVERSAL:
            return {
                "provider_stock_market": prov_name,
                "provider_currency": prov_name,
                "provider_crypto": prov_name
            }

        case ProviderT.CURR_CRYPTO:
            return {
                "provider_crypto": prov_name
            }

        case ProviderT.CURR_FOREX:
            return {
                "provider_currency": prov_name,
            }

        case ProviderT.STOCK_MARKET:
            return {
                "provider_stock_market": prov_name,
            }
