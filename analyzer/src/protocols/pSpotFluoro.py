import sys
sys.path.insert(0, './common')
import utils
from functools import reduce
import asyncio
import artifactCodec
import imageLib
import cv2
import itertools
import log

logger = log.getLogger('analyzer.src.protocols.pSpotFluoro')

argSchema = {
    "type": "object",
    "properties": {
        "minSpotDiameter": {
            "type": "number",
            "description": "The kernel size to use for initial low pass filtering. Roughly equates to the minimum spot size to detect.",
        },
        "maxSpotDiameter": {
            "type": "number",
            "description": "The neighborhood size to be used for min/max calulations. Roughly equates to the maximum spot size to detect."
        },
        "threshold": {
            "type": "number",
            "description": "The minimum difference between the min/max in a neighborhood to be counted as a spot"
        }
    }
}

codec = artifactCodec.ArtifactCodec()

async def execute(context):

    labelSpotRadius = int(context['args']['maxSpotDiameter'])

    async def processFrame(frame, index):

        await context['createAnalysisArtifact']("orig"+str(index)+".jpg", codec.arrayToJpg(frame))

        # data = cv2.blur(frame.image,(blurKernelRadius,blurKernelRadius))
        data = utils.chain([
            lambda i: imageLib.blur(i, (int(context['args']['minSpotDiameter'])//2)*2+1) # ensure odd
        ])(frame)

        spots = imageLib.findSpots(
            data, 
            int(context['args']['minSpotDiameter']), 
            int(context['args']['maxSpotDiameter']), 
            int(context['args']['threshold']))

        out = imageLib.constrainBrightness(frame.copy(), 0, 5000)
        out = imageLib.imageToColorImage(out)
        out = imageLib.invert(out)
        out = cv2.applyColorMap(out, cv2.COLORMAP_JET)

        for spot in spots:
            cv2.circle(out, (spot["x"],spot["y"]), labelSpotRadius, (255,255,255), 2)

        await context['createAnalysisArtifact']("maxima"+str(index)+".jpg", codec.arrayToJpg(out))

        spots = utils.chain([
            utils.cmap(lambda s: {**s, "frame":index}),
        ])(spots)

        return spots

    stack = codec.tiffStackToArray(await context['getScanArtifact']('pFluoro.tif'))

    spots = utils.flatten([await processFrame(f,i+1) for i,f in enumerate(stack)])

    await context['createAnalysisArtifact']("all_spots.csv", codec.dictArrayToCsv(spots))

    byFrame = [
        {"frame":key, "spots":len(list(group))}
        for key, group 
        in itertools.groupby(spots, lambda s: s["frame"])
    ]

    await context['createAnalysisArtifact']("frame_counts.csv", codec.dictArrayToCsv(byFrame))
