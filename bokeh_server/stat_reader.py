import asyncio
import redis
import json
from copy import deepcopy as copy
from collections import defaultdict

channel_names = []

class StatReader:
    def __init__(delay=0.01):
        self.ds = defaultdict(dict)
        channels = {chan:self.handler for chan in channel_names}
        self.r = redis.StrictRedis(...)
        self.p = r.pubsub(ignore_subscribe_messages=True)
        self.p.subscribe(**channels)
        self.delay = delay

    def start():
        self.th = self.p.run_in_thread(sleep_time=self.delay)
        self.th.start()

    def stop():
        self.th.stop()

    def handler(msg):
        if msg['type'] != 'message':
            return
        chan = msg['channel']
        data = json.loads(msg['data'].decode())
        name = data['name']
        self.ds[chan][name] = data


    @property
    def latest_data():
        return copy(self.ds)
