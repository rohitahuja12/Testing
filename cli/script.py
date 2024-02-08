import json
import os
import subprocess as sp
import sys
sys.path.insert(0, "./common")

async def handle (args):

    phxHome = os.environ['PHOENIX_HOME']
    # print('in py '+ os.environ['DB_HOST'])
    with open(phxHome+'/phx.json') as f:
        phxJson = json.load(f)

    scripts = phxJson['scripts']
    command = scripts[args['<scriptName>']]+' '+(' '.join(args['<scriptArgs>']))
    res = sp.call(command, shell=True, env=os.environ.copy())
