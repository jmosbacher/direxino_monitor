import aioredis
import collections
import time
import asyncio
ADDRESS = 'redis://localhost'

async def redis_publisher(queue, loop, channel='Data', data_name='value'):
    redis = await aioredis.create_redis_pool(
        ADDRESS,
        minsize=5, maxsize=10,
        loop=loop)
    try:
        while True:
            new = await queue.get()
            if isinstance(data, collections.Mapping):
                data = new
            else:
                data = {data_name: new}
            timestamp = time.time()
            data['publish_time'] = timestamp
            await redis.publish_json(channel, data)
            log.info('{} published to {} channel at {}'.format(data, channel, timestamp))
    finally:
        redis.close()
