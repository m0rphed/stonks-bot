from models import InstrumentEntity, StockInfo, CurrencyPairInfo


def msg_warning(msg: str) -> str:
    return "⚠️ " + msg


def msg_error(msg: str) -> str:
    return "⛔ " + msg


def msg_ok(msg: str) -> str:
    return "✅ " + msg


def stock_confirmation(ticker: str, price: str | int | float, exchange: str, data_provider: str) -> str:
    reply_message = f"Stock information:\n\n" \
                    f"Ticket: {ticker}\n" \
                    f"Price: {price}\n" \
                    f"Exchange: {exchange}\n" \
                    f"• provided by 👉 `{data_provider}`\n" \
                    f"\nIf this is the correct stock you want to track, click the button below to confirm."

    return reply_message


def stock_entity_confirmation(stk: InstrumentEntity) -> str:
    return stock_confirmation(
        stk.ticker,
        stk.price,
        stk.code_exchange,
        stk.data_provider
    )


def stock_api_confirmation(stk: StockInfo) -> str:
    return stock_confirmation(
        stk.symbol,
        stk.price,
        stk.exchange,
        stk.data_provider
    )


def curr_pair_confirmation(code_from: str, code_to: str, price: str | int | float, rate: str | int | float, exchange: str, data_provider: str) -> str:
    reply_message = f"Currency exchange pair information:\n\n" \
                    f"From `{code_from}` to `{code_to}`\n" \
                    f"Price: {price}\n" \
                    f"Exchange rate: {rate}\n"\
                    f"Exchange: {exchange}\n" \
                    f"• provided by 👉 `{data_provider}`\n" \
                    f"\nIf this is the correct exchange pair you want to track, click the button below to confirm."

    return reply_message


def curr_pair_entity_confirmation(curp: InstrumentEntity) -> str:
    code_from, code_to = curp.code_curr.split("_")
    return curr_pair_confirmation(
        code_from,
        code_to,
        curp.price,
        curp.exchange_rate,
        curp.exchange_rate,
        curp.data_provider
    )


def curr_pair_api_confirmation(curr: CurrencyPairInfo) -> str:
    return curr_pair_confirmation(
        curr.code_from,
        curr.code_to,
        curr.price_bid,  # TODO: should it be price BID or price ASK?
        curr.rate,
        curr.exchange,
        curr.data_provider
    )
