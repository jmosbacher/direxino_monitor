from threading import Thread
from stat_reader import StatReader
from functools import partial

data_reader = StatReader(('Arduino','Cryo1','Cryo2',))
cam_reader = StatReader(('Camera',))


def on_server_loaded(server_context):
    #FIXME: Setup the data readers and queues
    # Add a peridoc callback that updates display periodically from queues
    #server_context.add_next_tick_callback(callback)
    reader.start()

def on_server_unloaded(server_context):
    ''' If present, this function is called when the server shuts down. '''
    reader.stop()

def on_session_created(session_context):
    ''' If present, this function is called when a session is created. '''
    session_context['data_reader'] = reader
    print(session_context['data_reader'])

def on_session_destroyed(session_context):
    ''' If present, this function is called when a session is closed. '''
    pass
