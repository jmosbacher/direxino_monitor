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
from collections import defaultdict
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

attrs = {'channel': 'Channel',
         'name': 'Name',
         'value':'NaN',
         'color':'grey'}

dsources = {'stats': ColumnDataSource(),
      'camera': ColumnDataSource()}

def cam_update():
    data = doc.session_context['cam_reader'].latest_data
    return {'image':[np.random.randint(0, high=254, size=(100,100), dtype='uint8')]}


def stats_update():
    datadict = {name:[] for name in attrs}
    data = doc.session_context['data_reader'].latest_data
    for chan, messages in data.items():
        for name, msg in messages.items():
            for attr, default in attrs.items():
                datadict[attr].append(msg.get(attr,default))
    dsources['stats'].data = df.astype()

log.info(str(keys))
df = build_df(keys, datas)

imdata = read_camera()
ds['cam'] = ColumnDataSource(imdata)
lo = layout_builder.build_layout(ds, imdata)
doc.add_root(lo)
doc.title = "Monitor"
doc.add_periodic_callback(stats_update, UPDATE)
doc.add_periodic_callback(cam_update, UPDATE)
