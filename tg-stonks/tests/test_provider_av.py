import pytest
import pprint

import tg_stonks.utils.creds as creds
from tg_stonks.impl.alpha_vantage_provider import AlphaVantageAPI

pytest_plugins = (
    'pytest_asyncio',
)


@pytest.mark.asyncio
async def test_search_stock_market_not_empty():
    creds.load_env_file("../secret/.env")
    ticker = "AAPL"
    av_api = AlphaVantageAPI(creds.get_from_env("ALPHA_VANTAGE_TOKEN"))
    query_res = await av_api.search_stock_market(query=ticker)
    dumped = []
    for res in query_res:
        dumped.append(res.model_dump(mode="python"))
        assert res.data_provider == av_api.data_provider_name

    for x in dumped:
        pprint.pprint(x)

    assert not len(query_res) == 0
