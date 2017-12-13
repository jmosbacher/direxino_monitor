'''
For the Server to work,
Redis Server must be running and channels must be published to.

Start the server using "bokeh serve --bokeh_server.py"
'''
#FIXME This server has been hacked together to test bokeh
# Needs to be improved alot before it can replace TKinter app

#FIXME Consider removing dependency on tabulate

import numpy as np
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
import json
from functools import partial
from collections import OrderedDict
from tabulate import tabulate

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
MAXDATA = 100
NROWS = 2
NCOLS = 2
UPDATE = 500 #ms
doc = curdoc()

AVAILABLE = ['Arduino', 'Cryo1','Cryo2','Camera']

r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
log.info('Available channles: '+str(AVAILABLE))
p = r.pubsub()

tools = 'pan,wheel_zoom,xbox_select,reset'
sources = OrderedDict()
latest_values = OrderedDict()


imdata ={'image':[np.random.randint(0, high=254, size=(100,100), dtype='uint8')]}
imsrc = ColumnDataSource(imdata)
latest_text = PreText(text='', width=600, height=300)
lbl = PreText(text='Latest Data', width=600, height=50)
lt = column(widgetbox(lbl),widgetbox(latest_text))

def get_data_names(channel):
    names = []
    for _ in range(100):
        msg = p.get_message()
        if not msg:
            time.sleep(0.05)
            continue
        if msg['type']=='message' and msg['channel'].decode()==channel:
            data = json.loads(msg['data'])
            log.info('data: '+str(data))
            names = [key for key, val in data.items() if isinstance(val,(int,float))]
            break

    log.info('names: '+str(names))
    return names

def build_image_figure():
    label = PreText(text='Camera', width=350)

    fig = figure(plot_width=350,
                plot_height=350,
                x_range=(0, 100), y_range=(0, 100),
                responsive=True
                #tools=[],
                )
    fig.toolbar.logo = None
    fig.toolbar_location = None
    im = fig.image(image='image',x=0,y=0,dw=100,dh=100, source=imsrc)
    #log.info(str(im))
    col = column(widgetbox(label), fig)
    return col


def selection_changed_callback(src):
    def callback(attrname, old, new):
        if new in latest_values:
            val_dict = latest_values[new]
        else:
            return
        if 'time' in val_dict:
            T = val_dict['time']
        else:
            T = time.time()
        data = {'time': [T],
                'value': [val_dict['value']]}
        src.data = data
        if old in sources:
            sources.pop(old)
        sources[new] = src
    return callback

def build_figure(data_name, all_names):
    global sources
    data ={'value':[],
           'time': [],
           }
    src = ColumnDataSource(data)
    sources[data_name] = src
    sel = Select(value=data_name, options=all_names)
    sel.on_change('value', selection_changed_callback(src))

    ts = figure(plot_width=500,
                plot_height=150,
                tools=tools,
                x_axis_type='datetime',
                )

    line = ts.line(x='time', y='value',
                          source=src,
                          #line_color=np.random.choice(Spectral11),
                          #name=channel_name,
                          line_width=5,)
    col = column(widgetbox(sel), ts)
    return col

def build_layout(names):
    cam = build_image_figure()
    first_row = [cam, lt]
    rows = [first_row]
    #rows=[]
    for rn in range(NROWS):
        cols = []
        for cn in range(NCOLS):
            if (cn+rn)<len(names):
                cols.append(build_figure(names[rn+cn], names))
            else:
                break
        rows.append(cols)
    lo = layout(rows)
    return lo

def message_handler(message):
    if message is None:
        return
    if message['type']!='message':
        return
    #log.info(str(message))
    name = message['channel'].decode()
    data = json.loads(message['data'])
    T = time.time()
    for key, val in data.items():
        if key == 'time':
            T = val

    for key, val in data.items():
        new = OrderedDict()
        new['value'] = val
        new['time'] = T
        new['channel'] = name
        latest_values[key] = new


def update():
    message = True
    while message:
        message = p.get_message()
        if message:
            message_handler(message)

    for name, source in sources.items():
        if name not in latest_values:
            continue
        val =  latest_values[name]['value']
        if not isinstance(val, (float,int)):
            continue
        data = {'value':[val]}
        data['time'] = [latest_values[name].get('time', time.time())]
        source.stream(data, rollover=MAXDATA)


    if 'image' in latest_values:
        imdata = latest_values['image']
        if 'time' in imdata:
            T = imdata['time']
        else:
            T = time.time()
        img = np.asarray(imdata['value'])
        imsrc.data = {'image':[img]}
        #imsrc.trigger('change')

    rows = []
    headers =[]
    for key, val_dict in latest_values.items():
        row = [key]
        for val in val_dict.values():

            if isinstance(val, (float,int,str)):
                row.append(val)
            elif isinstance(val, list):
                row.append('list')
            else:
                row.append(' - ')
        rows.append(row)

        headers = ['Name']+[k for k in val_dict]
    if rows and headers:
        latest_text.text = tabulate(rows, headers=headers,
                                    tablefmt='fancy_grid', floatfmt='.4f')#'\n'.join(ls)


p.subscribe(*AVAILABLE)
names = []
for channel in AVAILABLE:
    names.extend(get_data_names(channel))
names = [name for name in names if 'time' not in name]
lo = build_layout(names)
doc.add_root(lo)
doc.title = "Monitor"
doc.add_periodic_callback(update, UPDATE)
try:

    pass
    #thread = p.run_in_thread(sleep_time=0.1)
except Exception as e:
    log.info(str(e))
    p.close()
