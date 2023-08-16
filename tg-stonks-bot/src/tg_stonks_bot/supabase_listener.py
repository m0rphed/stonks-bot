import asyncio
from typing import final, Callable

from loguru import logger
from realtime.channel import Channel
from realtime.connection import Socket

from database_listener import IDatabaseListener


@final
class SupabaseListener(IDatabaseListener):
    def __init__(self, sb_id: str, sb_key: str):
        self.URL = \
            f"wss://{sb_id}.supabase.co" \
            "/realtime/v1/websocket?" \
            f"apikey={sb_key}&vsn=1.0.0"

        self.soc = Socket(self.URL)
        # set default values
        self.ch: Channel | None = None
        self.ready_to_listen = False

    async def set_up(self, table_name: str):
        await self.soc._connect()
        self.ch = self.soc.set_channel(f"realtime:public:{table_name}")
        await self.ch._join()
        self.ready_to_listen = True

    async def start_listening(self):
        if not self.ready_to_listen or self.ch is None:
            raise RuntimeError(
                "Could not start listening when"
                " channels not set; set_up' method first"
            )

        # TODO: which "asyncio approach" is more appropriate in this case?
        # loop = asyncio.get_running_loop()
        # loop.create_task(self.soc._listen())
        # loop.create_task(self.soc._keep_alive())
        await asyncio.gather(self.soc._listen(), self.soc._keep_alive())

    def add_callback(self, event_str: str, cb_func: Callable, **kwargs):
        if not self.ready_to_listen or self.ch is None:
            raise RuntimeError(
                "Could not add callback for channel when"
                " channel not set up: run 'set_up' method first"
            )

        tg, db = kwargs.get("tg_client"), kwargs.get("database")
        if tg is None or db is None:
            raise RuntimeError(
                "Required kwargs not specified:"
                "\n  - 'tg_client': pyrogram tg-stonks-bot client (should be set up with credentials, but have not yet started)"
                "\n  - 'database': database provider impl. 'IDatabase'"
            )

        if asyncio.iscoroutinefunction(cb_func):
            def _wrapped(payload):
                loop = asyncio.get_running_loop()
                loop.create_task(
                    cb_func(payload, tg_client=tg, database=db)
                )

            self.ch.on(event_str, _wrapped)
            logger.info(f"<SbListener> added wrapped async callback on {event_str}")
        else:
            self.ch.on(event_str, lambda payload: cb_func(payload, tg_client=tg, database=db))
            logger.info(f"<SbListener> wrapped async callback on {event_str}")
