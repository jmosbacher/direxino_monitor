from bokeh.io import output_file, show, curdoc
from bokeh.models import ColumnDataSource, HoverTool, Range1d
from bokeh.plotting import figure
from bokeh.layouts import row, column, layout
from bokeh.models.widgets import PreText, Div
#from bokeh.sampledata.periodic_table import elements
from bokeh.layouts import widgetbox
from bokeh.transform import dodge, factor_cmap
import random
import numpy as np
#from collections import Counter
import pandas as pd

def formatter(x):
    if isinstance(x, float):
        return round(x,3)
    else:
        return x

def build_header():
    img = Div(text="""<h1 style='text-align:left;font-size:40px;'> Direxino</h1> <p style="float: center;">
              <img src='bokeh_server/static/Snail.png' hspace="20px" vspace="10px" width='140px,height='140px'> </p>
            <h1 style='text-align:left;font-size:40px;'> Control</h1> <hr>""", width=500, height=300)

    return widgetbox(img)

def build_cam_view(source, imdata):
    label = PreText(text='Camera', width=300)

    fig = figure(plot_width=300,
                plot_height=300,
                x_range=(0, 100), y_range=(0, 100),
                responsive=True)

    fig.toolbar.logo = None
    fig.toolbar_location = None
    fig.xaxis.major_tick_line_color = None  # turn off x-axis major ticks
    fig.xaxis.minor_tick_line_color = None  # turn off x-axis minor ticks
    fig.yaxis.major_tick_line_color = None  # turn off y-axis major ticks
    fig.yaxis.minor_tick_line_color = None  # turn off y-axis minor ticks
    fig.xaxis.major_label_text_font_size = '0pt'  # preferred method for removing tick labels
    fig.yaxis.major_label_text_font_size = '0pt'  # preferred method for removing tick labels

    im = fig.image(image='image',x=0,y=0,dw=100,dh=100, source=source)
    #log.info(str(im))
    col = column(widgetbox(label), fig)
    return fig

def build_stat_boxes(source, data, ycol, valcol,**kwargs ):
    ttnames=kwargs.get('tooltips', None)
    xsize=kwargs.get('xsize', 100)
    ysize=kwargs.get('ysize', 75)
    title=kwargs.get('title', '')
    xrange = [str(x) for x in set(data['xidx'])]
    yrange = list(data[ycol].value_counts(ascending=True).index) #[str(x) for x in set(data[ycol])]

    source.data = data.applymap(formatter).to_dict('list')

    p = figure(plot_width=xsize*(len(xrange)+1), plot_height=ysize*(len(yrange)+1), title=title,
           naxrange, y_range=yrange, toolbar_location=None, tools="")
    p.rect('xidx', ycol, 0.9, 0.9, source=source, fill_alpha=0.5,)

    text_props = {"source": source, "text_align": "center", "text_baseline": "middle"}

    if 'name' in data:
        y = dodge(ycol, 0.3, range=p.y_range )
        r1 = p.text(x='xidx', y=y, text="name", **text_props)
        r1.glyph.text_font_style="bold"
        #r1.glyph.text_baseline="bottom"
    r2 = p.text(x='xidx', y=ycol, text=valcol, **text_props)
    if 'color' in data:
        r2.glyph.text_color = data['color']

    if ttnames is None:
        names = data.columns
    else:
        names = ttnames
    ttips = [(name.title(),'@{}'.format(name)) for name in names]
    p.add_tools(HoverTool(tooltips = ttips))

    p.toolbar.logo = None
    p.toolbar_location = None
    p.xaxis.major_tick_line_color = None  # turn off x-axis major ticks
    p.xaxis.minor_tick_line_color = None  # turn off x-axis minor ticks
    p.yaxis.major_tick_line_color = None  # turn off y-axis major ticks
    p.yaxis.minor_tick_line_color = None  # turn off y-axis minor ticks
    p.xaxis.major_tick_line_color = None  # turn off y-axis minor ticks
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.xaxis.major_label_text_font_size = '0pt'  # preferred method for removing tick labels
    #p.yaxis.major_label_text_font_size = '0pt'  # preferred method for removing tick labels
    p.axis.major_label_standoff = 0
    #p.legend.orientation = "horizontal"
    #p.legend.location ="top_center"

    return p, source

def build_stream(data,source, scale=0.2):
    yrange = [str(y) for y in data['full_name']]
    p = figure(plot_width=800, plot_height=800, y_range=yrange, x_axis_type='datetime',
               title="Time dependence")
    xpos = data['time']
    ym = np.mean([d for d in data['value'] if isinstance(d, (int,float))])
    xs, ys, names = [],[],[]
    for x,y,name in zip(data['time'],data['value'],data['full_name']):
        if isinstance(y, (int,float)):
            xs.append(x)
            ys.append(scale*y)
            names.append(name)

    ypos = list(zip(names, ys))
    source.data = dict(xpos=xs, ypos=ypos)
    p.circle(x='xpos', y='ypos',  source=source, alpha=0.3)

    p.x_range.range_padding = 0
    p.ygrid.grid_line_color = None
    return p

def build_layout(ds,df, imdata):
    stats, _ = build_stat_boxes(ds['stats'], df, 'channel', 'value')
    #stream = build_stream(df.to_dict('list'), ds['stream'])
    head = build_header()
    cam = build_cam_view(ds['cam'], imdata)
    return column(row(head, cam), stats)
