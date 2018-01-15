import aioredis
import collections
import time
import asyncio
ADDRESS = 'redis://localhost'

async def publish_value(redis,channel, name, value):
    data = {'name': name,
            'value': value,
            'channel':channel,
            'publish_time': time.time()}
    await redis.publish_json(channel, data)
    log.info('{} published to {} channel at {}'.format(data, channel, timestamp))

async def redis_publisher(queue, loop, channel='Data', data_name='value'):
    redis = await aioredis.create_redis_pool(
        ADDRESS,
        minsize=5, maxsize=10,
        loop=loop)
    try:
        while True:
            new = await queue.get()
            timestamp = time.time()
            if isinstance(data, collections.Mapping):
                if all([x in new for x in ['name','value']]:
                    new['channel'] = channel
                    new['publish_time'] = time.time()
                    await redis.publish_json(channel, new)
                else:
                    for key, value in new:
                        await publish_value(redis,chanel, key, value)
            else:
                await publish_value(redis, cahnnel, data_name, new)
    finally:
        redis.close()
