import emoji


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
