import os
os.environ["COMPONENT_CLASS"] = "cli"

usage = '''
Usage:
    phx admin install
    phx admin uninstall
    phx api create <collection> <jsonFilePath>
    phx api delete <collection> <docId>
    phx api get    <collection> <docId>
    phx api getall <collection> [<filters>]
    phx api login
    phx api update <collection> <jsonFilePath>
    phx controller-gui <configPath>
    phx create plates <barcodesFilePath> <productId>
    phx create scan <scanDocumentPath> <metadataPath> <stackPath>
    phx dumpanalysis <analysisId> <outputDirPath>
    phx dumpscan <scanId> <outputDirPath>
    phx galJsonToProduct <galJsonPath>
    phx parse gal <galFilePath> 
    phx parse gal <galFilePath> <outputFilePath>
    phx plot-product <productPath> <outputFilePath>
    phx reader-repl <readerSerialNumber>
    phx run <scriptName> [<scriptArgs>...]
    phx view-image-stream <cameraStreamTransport>
    phx spotcheck <plateID> <imageFilePath> [<outputPath>] [<qcParams>]
'''

from docopt import docopt
args = docopt(usage)

import api
import admin
import gal
import galjsonconverter
import script
import dumpscan
import dumpanalysis
import asyncio
import plot
import createplates
import createScanFromStack
import spotcheck
import controller_gui.controller_gui as controller_gui
import image_stream_viewer.viewer as stream_viewer

if args["api"]:
    asyncio.run(api.handle(args))

elif args["admin"]:
    asyncio.run(admin.handle(args))

elif args["gal"]:
    asyncio.run(gal.handle(args))

elif args["plot-product"]:
    asyncio.run(plot.handle(args))

elif args["run"]:
    asyncio.run(script.handle(args))

elif args["dumpscan"]:
    asyncio.run(dumpscan.handle(args))

elif args["dumpanalysis"]:
    asyncio.run(dumpanalysis.handle(args))

elif args["reader-repl"]:
    asyncio.run(live.handle(args))

elif args["galJsonToProduct"]:
    asyncio.run(galjsonconverter.handle(args))

elif args["create"] and args["plates"]:
    asyncio.run(createplates.handle(args))

elif args["create"] and args["scan"]:
    asyncio.run(createScanFromStack.handle(args))

elif args["controller-gui"] and args["<configPath>"]:
    asyncio.run(controller_gui.handle(args))

elif args["view-image-stream"] and args["<cameraStreamTransport>"]:
    asyncio.run(stream_viewer.handle(args))

elif args["spotcheck"]:
    asyncio.run(spotcheck.handle(args))