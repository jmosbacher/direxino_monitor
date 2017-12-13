import asyncio
import logging
from readers import SocketReader, producer
from publishers import redis_publisher

IP = '127.0.0.1'
PORT= 25002
READ_EVERY = 1 #seconds

if __name__=='__main__':
    queue = asyncio.Queue()
    settings['ip'] = IP
    settings['port'] = PORT
    settings['command'] = b''
    settings['buffer_size'] = 1024
    settings['mode'] = 'JSON'
    settings['sep'] = b'EOF'

    loop = asyncio.get_event_loop()
    reader = SocketReader(settings,loop=loop)
    produce = producer(reader, queue, DELAY=READ_EVERY)
    publish = redis_publisher(queue, channel='Arduino')
    loop.run_until_complete(asyncio.gather(produce,publish))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.close()
