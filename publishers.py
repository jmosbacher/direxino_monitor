import aioredis

async def redis_publisher(queue, channel='Data', data_name='value'):
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
