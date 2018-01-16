import asyncio
import redis
import json
from copy import deepcopy as copy
from collections import defaultdict

class StatReader:
    def __init__(self,channel_names,delay=0.01):
        self.ds = defaultdict(list)
        channels = {chan:self.handler for chan in channel_names}
        self.r = redis.StrictRedis(...)
        self.p = self.r.pubsub(ignore_subscribe_messages=True)
        self.p.subscribe(**channels)
        self.delay = delay

    def start(self):
        self.th = self.p.run_in_thread(sleep_time=self.delay)

    def stop(self):
        self.th.stop()

    def handler(self, msg):
        if msg['type'] != 'message':
            return
        chan = msg['channel']
        data = json.loads(msg['data'].decode())
        name = data.get('name','Unknown')
        self.ds[chan][name] = data


    @property
    def latest_data(self):
        return copy(self.ds)
