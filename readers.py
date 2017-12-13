import asyncio
import json
import time
import logging
import contextlib
log = logging.getLogger(__name__) # Log under current position in hierarchy

class SocketReader:
    def __init__(self, settings, loop=None,):
        self.ip = settings['ip']
        self.port = settings['port']
        self.command = settings.get('command', b'')
        self.buffer_size = settings.get('buffer_size', 1024)
        self.mode = settings.get('mode', None)
        self.sep = settings.get('sep', b'')
        self.name = settings.get('name', None)

        if loop is None:
            self.loop = asyncio.get_event_loop()

        self.connected = False

    async def __aenter__(self):
        await self.connect()
        return self.read_data

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.disconnect()
        if any(exc_type, exc_value, traceback):
            info = [' '.join('='*15,'Exception Raised', '='*15)]
            info.append('Exception Type: {}'.format(exc_type))
            info.append('Exeption Value: {}'.format(exc_value))
            info.append('Traceback: {}'.format(traceback))
            info.append(['=']*40)
            log.info('\n'.join(info))
        return True

    async def connect(self):
        self.reader, self.writer = \
            await asyncio.open_connection(self.ip, self.port, loop=self.loop)
        self.connected = True

    def disconnect(self):
        self.writer.close()
        self.connected = False

    def decode(data):
        if self.mode=='JSON':
            return json.loads(data.decode())

        elif self.mode=='RSTRIP':
            return data.decode().rstrip()
        else:
            return data.decode()

    async def read_data():
        if type(self.command)==type(b''):
            self.writer.write(self.command)
        else:
            self.writer.write(self.command.encode())
        await self.writer.flush()

        if self.sep:
            data = await self.reader.readuntil(sep)
        else:
            data = await self.reader.read(self.buffer_size)

        return self.decode(data)


async def producer(reader, queue, DELAY=1):
    with reader as read:
        while True:
            timer = asyncio.ensure_future(asyncio.sleep(DELAY))
            data = await read()
            await queue.put(data)
            await asyncio.wait_for(timer)

async def collector(readers, queue, DELAY=1):
    queues = []
    producers = []
    for reader in readers:
        q = asyncio.Queue()
        queue.append(q)
        produce = producer(reader, q, DELAY=DELAY)
        producers.append(asyncio.ensure_future(produce))
    while True:
        for q,r in zip(queues, readers):
            data[r.name] = await q.get()
        await queue.put(data)
