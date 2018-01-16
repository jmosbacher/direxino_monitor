from subprocess import run

scripts = ['publish_arduino', 'publish_cam', 'publish_cryo1','publish_cryo2']

run(['redis-server'])

def run_script(name):
    run(['python', name+'.py'])

for script in scripts:
    run_script(script)

run(['bokeh','serve','--show','bokeh_server'])
