import subprocess as sp
import os

async def handle (args):

    if args.get("install", None):
        # install docker
        home = os.environ["PHOENIX_HOME"]
        sp.run(home+"/cli/install/ubuntu.docker.sh")
