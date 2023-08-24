from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from tg_stonks.providers.protocols import IDataProvider
from tg_stonks.providers.provider_type import ProviderT
from tg_stonks.database.user_settings import DataProviderConfig
from tg_stonks.bot.formatting import msg_error


def btn_cancel(callback_data_suffix: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        "❌ Cancel",
        callback_data=f"canceled {callback_data_suffix}"
    )


def btn_confirm(cb_data_suffix: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        "✅ Confirm",
        callback_data=cb_data_suffix
    )


def btn_set_prov(btn_text: str, prov_t_str: str, prov_name: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        btn_text,
        callback_data=f"confirmed --cmd prov {prov_t_str} {prov_name}"
    )


def markup_confirmation(cb_data_confirmed: str, cb_data_canceled: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[
            btn_confirm(cb_data_confirmed),
            btn_cancel(cb_data_canceled)
        ]]
    )


def markup_chose_provider(prov: IDataProvider) -> tuple[str, InlineKeyboardMarkup]:
    match prov.provider_type:
        case ProviderT.STOCK_MARKET:
            msg = "Set this provider for --stock market-- data 🚀📈🦬"
            markup = InlineKeyboardMarkup(
                [[
                    btn_set_prov("Set for stock market", ProviderT.STOCK_MARKET.value, prov.provider_name),
                    btn_cancel("--cmd prov")
                ]]
            )
            return msg, markup

        case ProviderT.CURR_FOREX:
            msg = "Set this provider for --foreign currency exchange-- data 💹💲💱"
            markup = InlineKeyboardMarkup(
                [[
                    btn_set_prov("Set for forex market", ProviderT.CURR_FOREX.value, prov.provider_name),
                    btn_cancel("--cmd prov")
                ]]
            )
            return msg, markup

        case ProviderT.CURR_CRYPTO:
            msg = "Set this provider for --cryptocurrency-- data ₿👩🏻‍💻🌐"
            markup = InlineKeyboardMarkup(
                [[
                    btn_set_prov("Set for crypto market", ProviderT.CURR_CRYPTO.value, prov.provider_name),
                    btn_cancel("--cmd prov")
                ]]
            )
            return msg, markup

        case ProviderT.UNIVERSAL:
            msg = "You can set this provider for --all kinds-- of data 📈💹₿"
            markup = InlineKeyboardMarkup(
                [
                    [btn_set_prov("Set for stock market", ProviderT.STOCK_MARKET.value, prov.provider_name)],
                    [btn_set_prov("Set for forex market", ProviderT.CURR_FOREX.value, prov.provider_name)],
                    [btn_set_prov("Set for crypto market", ProviderT.CURR_CRYPTO.value, prov.provider_name)],
                    [btn_set_prov("Set for everything", ProviderT.UNIVERSAL.value, prov.provider_name)],
                    [btn_cancel("--cmd prov")]
                ]
            )
            return msg, markup


async def reply_running_without_providers(message: Message):
    await message.reply(msg_error("Bot running without any data providers"))


def make_prov_settings(prov_t_value: ProviderT, conf: DataProviderConfig) -> dict:
    match prov_t_value:
        case ProviderT.UNIVERSAL:
            return {
                "provider_stock_market": conf.model_dump(),
                "provider_currency": conf.model_dump(),
                "provider_crypto": conf.model_dump()
            }
        case ProviderT.CURR_CRYPTO:
            return {
                "provider_stock_market": None,
                "provider_currency": None,
                "provider_crypto": conf.model_dump()
            }

        case ProviderT.CURR_FOREX:
            return {
                "provider_stock_market": None,
                "provider_currency": conf.model_dump(),
                "provider_crypto": None
            }

        case ProviderT.STOCK_MARKET:
            return {
                "provider_stock_market": conf.model_dump(),
                "provider_currency": None,
                "provider_crypto": None
            }

        case _:
            raise ValueError(
                "Specified provider type is incorrect",
                prov_t_value
            )
