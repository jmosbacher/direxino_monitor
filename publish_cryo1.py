import asyncio
import logging
from readers import SocketReader, collector
from publishers import redis_publisher

IP = '192.168.1.4' #18A
PORT = 5000
READ_EVERY = 1 #seconds

COMMANDS = {'ch{}:name': "input {}:NAMe?",
            'ch{}:value': "input? {}"
            'ch{}:units': "input {}:UNITs?",
            'ch{}:sensor': "input {}:SENSor?"}

if __name__=='__main__':
    settings['ip'] = IP
    settings['port'] = PORT
    settings['buffer_size'] = 1024
    settings['mode'] = 'RSTRIP'
    settings['sep'] = b'EOF'

    loop = asyncio.get_event_loop()
    queue = asyncio.Queue()

    producers = []
    for k in range(CHANNELS):
        readers = []
        for name, command in COMMANDS.items():
            settings['name'] = name.format(k)
            settings['command'] = command.format(k)
            reader = SocketReader(settings,loop=loop)
        produce = collector(readers, queue, DELAY=READ_EVERY)
        producers.append(produce)

    publish = redis_publisher(queue, loop, channel='Cryo1')
    loop.run_until_complete(asyncio.gather(*producers,publish))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.close()
