# direxino_monitor
The Direxino monitor currently consists of three conceptual tasks:
  - Reading data from data servers
  - Publishing the data to a Redis server
  - Serving published data in realtime via http requests

Future tasks will included:
  - Monitoring data servers
  - Sending alerts

Dependencies:
  - asyncio
  - redis
  - aioredis
  - redis server
  - numpy
  - Bokeh (for the http server)
  - tabulate
