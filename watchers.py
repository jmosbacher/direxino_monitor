import asyncio
import json
import time
import logging
import contextlib
log = logging.getLogger(__name__) # Log under current position in hierarchy

#FIXME Under Construnction!

class IPWatcher:
    def __init__(self, clients, loop=None):
        self.addresses = addresses
        self.timeout = timeout
        if loop is None:
            self.loop = asyncio.get_event_loop()

    def watch_all(self):
        for address in

    async def watch(self, ip, port):
        pass

    async def connect(self):
        await loop.
