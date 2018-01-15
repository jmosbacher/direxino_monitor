import numpy as np
import pandas as pd
import logging
from bokeh.io import curdoc
from bokeh.layouts import row, column, layout
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import PreText, Select
from bokeh.plotting import figure

from bokeh.io import output_file, show
from bokeh.layouts import widgetbox
from bokeh.models.widgets import CheckboxGroup, CheckboxButtonGroup, Select
from bokeh.palettes import Spectral11
import time
import redis
import layout_builder
import json
from functools import partial
#from collections import Counter, OrderedDict
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
MAXDATA = 1000
NROWS = 2
NCOLS = 2
UPDATE = 300 #ms
HSHIFT = 0.5
doc = curdoc()

stat_channels = ['harmonic', 'random_number','ping_pong',]
cam_channel = 'Camera'
r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
log.info('Available channles: '+str(stat_channels))
stats = r.pubsub()
cam = r.pubsub()
stats.subscribe(*stat_channels)
cam.subscribe(cam_channel)
data_keys = {chan:set() for chan in stat_channels}
#data = {'name':[], 'value':[], 'channel':[]}
last_stats = {'name':[], 'value':[], 'channel':[]}
ds = {}
def formatter(x):
    if isinstance(x, float):
        return round(x,3)
    else:
        return x

def make_indexer(datas):
    xindexer = {}
    for chan, rows in datas.items():
        xindexer[chan] = {}
        for n, name in enumerate(rows):
             xindexer[chan][name] = n+ HSHIFT
    return xindexer

def make_index(indexer, df):
    idx = []
    for chan, name in zip(df['channel'].tolist(), df['name'].tolist()):
        idx.append(indexer[chan][name])
        log.info('{} {} {}'.format(chan, name, idx[-1]))
    return idx

def read_camera():
    for _ in range(10):
        message = cam.get_message()
        if message and message['type']=='message':
            return json.loads(message['data'].decode())
        else:
            time.sleep(UPDATE/10000)
    return {'image':[np.random.randint(0, high=254, size=(100,100), dtype='uint8')]}

def read_new_messages(ntries=1):
    message = True
    datas = {chan:{} for chan in stat_channels}
    for _ in range(ntries):
        while message:
            message = stats.get_message()
            if message and message['type']=='message':
                #log.info('Received message: {}'.format(message))
                channel = message['channel'].decode()
                data = json.loads(message['data'].decode())
                datas[channel][data['name']] = data
        time.sleep(0.05)

    return datas

def all_keys(datas):
    keys = set()
    for chan, rows in datas.items():
        for name, row in rows.items():
            keys.update(row.keys())
    return keys



def build_df(keys, datas):
    ddict = {key:[] for key in keys}
    for chan, rows in datas.items():
        for name, row in rows.items():
            for key in keys:
                ddict[key].append(row.get(key,-999))
    df = pd.DataFrame(data=ddict)
    indexer = make_indexer(datas)
    df['xidx'] = make_index(indexer, df)
    df['full_name'] = df['channel']+':'+df['name']

    #log.info(str(df))
    return df

def stats_update():
    global last_stats
    datas = read_new_messages(int(5000/UPDATE))
    if datas:
        df = build_df(keys, datas)
        last_stats = df.to_dict('list')
        ds['stats'].data = df.applymap(formatter).to_dict('list')

def stream_update():
    log.info('updating')
    xs, ys, names = [],[],[]
    for x,y,name in zip(last_stats['time'],last_stats['value'],last_stats['full_name']):
        if isinstance(y, (int,float)):
            xs.append(x)
            ys.append(0.2*y)
            names.append(name)

    ypos = list(zip(names, ys))
    data = dict(xpos=xs, ypos=ypos)
    log.info(str(data))
    ds['stream'].stream(data, MAXDATA)
    log.info('updated')

def cam_update():
    ds['cam'].data = read_camera()

def all_channels_have_data(datas):
    for chan in stat_channels:
        if not len(datas[chan]):
            return False
    return True

datas = {}
for _ in range(100):
    datas.update(read_new_messages(10))
    if all_channels_have_data(datas):
        log.info(str(datas))
        break
    else:
        time.sleep(0.05)
else:
    raise Exception('Cant read stats data')
keys = all_keys(datas)
if not keys:
    raise Exception('Cant read stats data')

log.info(str(keys))
df = build_df(keys, datas)
ds['stats'] = ColumnDataSource(df)
ds['stream'] = ColumnDataSource(df)
imdata = read_camera()
ds['cam'] = ColumnDataSource(imdata)
lo = layout_builder.build_layout(ds, df, imdata)
doc.add_root(lo)
doc.title = "Monitor"
doc.add_periodic_callback(stats_update, UPDATE)
doc.add_periodic_callback(cam_update, UPDATE)
doc.add_periodic_callback(stream_update, UPDATE)
