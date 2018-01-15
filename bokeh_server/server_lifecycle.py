from collections import Queue, OrderedDict
from threading import Thread
from utils import ThreadSafeObject
from stat_reader import read_stats
from functools import partial
latest_data = ThreadSafeObject({})



def on_server_loaded(server_context):
    #FIXME: Setup the data readers and queues
    # Add a peridoc callback that updates display periodically from queues
    #server_context.add_next_tick_callback(callback)
    callback = partial(read_stats, latest_data)
    server_context.add_periodic_callback(callback, period_milliseconds)

def on_server_unloaded(server_context):
    ''' If present, this function is called when the server shuts down. '''
    pass

def on_session_created(session_context):
    ''' If present, this function is called when a session is created. '''
    session_context['latest_data'] = latest_data

def on_session_destroyed(session_context):
    ''' If present, this function is called when a session is closed. '''
    pass
