import sys
sys.path.insert(0, "./common")
import dbclient
import imageLib as im
import tempfile
from artifactCodec import ArtifactCodec
import json
import os
import zipfile
import io
import shutil

async def handle(args):
    codec = ArtifactCodec()
    scanDoc = args["<scanDocumentPath>"]
    metadataPath = args["<metadataPath>"]
    tempDir = tempfile.TemporaryDirectory()

    #copy metadata file to tempDir
    shutil.copy(metadataPath,tempDir.name)

    #load stack and save out individual tif files to a temp dir
    stack =  im.loadStack(path=args["<stackPath>"])
    for i,s in enumerate(stack):
        name = os.path.join(tempDir.name, stack[i].position)
        codec.saveTiff(name,stack[i].image)

    #write the zip file to a buffer
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in os.listdir(tempDir.name):
            file_path = os.path.join(tempDir.name, file)
            # Check if it's a file and not a directory
            if os.path.isfile(file_path):
                zipf.write(file_path, os.path.basename(file_path))
    buffer.seek(0)

    #load the scan json
    scanFile = open(scanDoc)
    scanDocJson = json.load(scanFile)
    #create scan doc
    scanDocResult = await dbclient.create('scans',scanDocJson)
    scanId = scanDocResult['_id']
    print(f"Created scan from stack, id: {scanId}")

    #add attachment
    await dbclient.createAttachment("scans",scanId,buffer,"results")