import sys
sys.path.insert(0, './common')
sys.path.insert(0, './common/spot_intensity_detector')
import utils
import asyncio
import imageLib
import cv2
from zipfile import ZipFile
import io
import math
import numpy as np
import random
from curveFitter import fit4, fit5, logistic4, logistic4Inverse, logistic5, logistic5Inverse,  getValidRanges, findOverlaps
from statistics import mean, stdev
import log
import artifactCodec
from coords import Point
import plotting as plt
import heatmapLib
from regionHelper import regions, pointsToPixelSpace
from scipy.stats import f
from pArrayFluoro_lib import *

from detector import *
import json

from productHelper import getAnalyteSpotMap
from pArrayFluoro_lib import markOutliers

import statistics

from numpy.polynomial.chebyshev import Chebyshev as cheby
from numpy.polynomial.chebyshev import chebfit

from datetime import datetime

logger=log.getLogger('analyzer.src.protocols.pArrayFluoro')

argSchema = {
    "type": "object"
}

codec = artifactCodec.ArtifactCodec()

async def execute(context):

    summaryResultsZip = {}
    processReport = []
    logger.info("Executing pArrayFluoro Analysis")
    processReport.append(f"pArrayFluoro Analysis started at {datetime.utcnow()} UTC\n")
    processReport.append("VERSION 0.92 as of 1-24-2024")
    processReport.append("")

    analysisName = context['analysis']['name']
    productName = context['analysis']['productName']
    scanName = context['analysis']['scanName']

    processReport.append(f"Analysis Name: {analysisName}")
    processReport.append(f"Scan Name: {scanName}")
    processReport.append(f"Product Name: {productName}")
    processReport.append("")

    #step 1:  collect data and set up experiment

    def remove_entries_by_value(list_of_dicts, key_to_check, value_to_remove):
        return [d for d in list_of_dicts if d.get(key_to_check) != value_to_remove]

    # which wells are we analyzing?
    allWells = context['args']['wells']
    #remove "empty" wells
    experimentWells = remove_entries_by_value(allWells,"type","empty")

    wellList = [ f"{experimentWell['row']}{experimentWell['column']} ({experimentWell['label']})"
                       for experimentWell in experimentWells ]
    wellListString = ', '.join(wellList)
    processReport.append(f"The following wells are being analyzed: {wellListString}\n")

    def check_for_standards(experimentWells):
        result = False
        for e in experimentWells:
            if e['type'] == 'standard':
                result = True
        return result

    hasStandards = check_for_standards(experimentWells)

    # load all the scan image metadata
    async def loadImageMetadata():
        imMetadata = await context['getScanArtifact']("imageMetadata.json")
        return imMetadata

    imageMetadata = await loadImageMetadata()
    imageMetadataDict = json.loads(imageMetadata)

    #convert json to img detail objects
    imageMetadataList = getImageDetails(imageMetadataDict,experimentWells)

    productDict = context['product']
    argsDict = context['args']
    spotMap = getAnalyteSpotMap(productDict)
    listOfAnalytes = list(argsDict['initialConcentrations'].keys())

    logger.info(f"ARGS: {argsDict}")
    logger.info(f"PROD: {productDict}")

    dictOfAnalytes = argsDict['initialConcentrations']
    processReport.append("")
    processReport.append(f"Initial concentrations of analytes: {str(dictOfAnalytes)}")
    processReport.append(f"Dilution factor: {context['args']['standardDilutionFactor']}")

    #assuming that x = y dimensions for now
    imageDimensionUm = 4400

    try:
        archive = createArchive()

        processReport = []
        logger.info("Executing pArrayFluoro Analysis")
        processReport.append(f"pArrayFluoro Analysis started at {datetime.utcnow()} UTC\n")
        processReport.append("VERSION 0.9 as of 10-23-2023")
        processReport.append("")

        analysisName = context['analysis']['name']
        productName = context['analysis']['productName']
        scanName = context['analysis']['scanName']

        processReport.append(f"Analysis Name: {analysisName}")
        processReport.append(f"Scan Name: {scanName}")
        processReport.append(f"Product Name: {productName}")
        processReport.append("")

        #step 1:  collect data and set up experiment

        def remove_entries_by_value(list_of_dicts, key_to_check, value_to_remove):
            return [d for d in list_of_dicts if d.get(key_to_check) != value_to_remove]

        # which wells are we analyzing?
        allWells = context['args']['wells']
        #remove "empty" wells
        experimentWells = remove_entries_by_value(allWells,"type","empty")

        wellList = [ f"{experimentWell['row']}{experimentWell['column']} ({experimentWell['label']})"
                           for experimentWell in experimentWells ]
        wellListString = ', '.join(wellList)
        processReport.append(f"The following wells are being analyzed: {wellListString}\n")

        def check_for_standards(experimentWells):
            result = False
            for e in experimentWells:
                if e['type'] == 'standard':
                    result = True
            return result

        hasStandards = check_for_standards(experimentWells)

        # load all the scan image metadata
        async def loadImageMetadata():
            imMetadata = await context['getScanArtifact']("imageMetadata.json")
            return imMetadata

        imageMetadata = await loadImageMetadata()
        imageMetadataDict = json.loads(imageMetadata)

        #convert json to img detail objects
        imageMetadataList = getImageDetails(imageMetadataDict,experimentWells)

        productDict = context['product']
        argsDict = context['args']
        spotMap = getAnalyteSpotMap(productDict)
        listOfAnalytes = list(argsDict['initialConcentrations'].keys())

        logger.info(f"ARGS: {argsDict}")
        logger.info(f"PROD: {productDict}")

        dictOfAnalytes = argsDict['initialConcentrations']
        processReport.append("")
        processReport.append(f"Initial concentrations of analytes: {str(dictOfAnalytes)}")
        processReport.append(f"Dilution factor: {context['args']['standardDilutionFactor']}")

        # def markOutliers(analyteSpots):
        #     results = analyteSpots
        #     if (len(analyteSpots) >= 3):
        #         outlierResultList = dixon_test( [s['intensity'] for s in analyteSpots])
        #         for a in analyteSpots:
        #             if a['intensity'] in outlierResultList:
        #                 a['outlier'] = 1
        #             else:
        #                 a['outlier'] = 0
        #     return results

        #assuming that x = y dimensions for now
        imageDimensionUm = 4400
        try:
            #TBD: Assuming a square image.  Modify to allow for scaling along both x and y
            #imageDimensionUm = imageMetadataDict['fovSizeXUm']
            imageDimensionUm = imageMetadataDict['metadata'][0]["fovSizeXUm"]
        except:
            logger.info(f"No fovSizeXUm found in imageMetadata.  Defaulting to: {imageDimensionUm}")

        signalIntensityAlgorithm = "mean-threshold"
        try:
            signalIntensityAlgorithm  = argsDict['signalIntensityAlgorithm']
            logger.info(f"Signal intensity calculation algorithm param: {signalIntensityAlgorithm}")
        except:
            logger.info(f"No signal calculation algorithm found in arguments.  Defaulting to: {signalIntensityAlgorithm}")

        processReport.append("")
        processReport.append(f"Signal intensity calculation algorithm: {signalIntensityAlgorithm}")
        logger.info(f"Analyte list:{listOfAnalytes}")
        processReport.append("")
        # for each well, retrieve the associated image
        async def loadImageByWell(well):
            bytes = await context['getScanArtifact'](f'{well["row"]}{well["column"]}')
            img = codec.tiffToArray(bytes)
            return img

        imageList = await asyncio.gather(*[
            loadImageByWell(w) for w in experimentWells
        ])

        #TBD:  Error handling around images existence
        imgXPx, imgYPx = np.shape(imageList[0])

        umPerPx = imageDimensionUm / imgXPx

        spotDiameterUm = productDict['spotDiameterUm']
        spotDistanceUm = productDict['spotDistanceUm']

        spotDiameterPx = int(spotDiameterUm / umPerPx)
        spotDistancePx = int(spotDistanceUm / umPerPx)

        resIntensities, resStats, annotatedImages = detect_intensities(imageList,
                                                                   imageMetadataList,
                                                                   { 'spotDiameterPx':spotDiameterPx,
                                                                     'spotDistancePx':spotDistancePx,
                                                                     'signalIntensityAlgorithm':signalIntensityAlgorithm})

        processReport.append(f"Successfully computed intensities from {len(annotatedImages)} images.")
        processReport.append("")

        createArtifact = context['createAnalysisArtifact']
        csvStatResults = codec.dataclassObjectArrayToCsv(resStats)
        csvIntensityResults = codec.dataclassObjectArrayToCsv(resIntensities)
        await createArtifact("allSpots_stats.csv", csvStatResults)
        archive = addToArchive(archive,'allSpots_stats.csv',csvStatResults)

        for key,value in annotatedImages.items():
            annotatedImage = codec.compressJpg(codec.arrayToJpg(value),30)
            await createArtifact(f"annotatedWellImage_{key}.jpg",annotatedImage)
            archive = addToArchive(archive,f'annotatedWellImage_{key}.jpg',annotatedImage)

        def getWellDescriptors(wellList,wellRow, wellColumn):
            for r in wellList:
                if r['row'] == str(wellRow) and r['column'] == str(wellColumn):
                    return r['replicateIndex'], r['label'], r['type']

        allSpots = []
        for s in resIntensities:
            replicateIndex,label,type = getWellDescriptors(experimentWells,s.wellRow,s.wellColumn)
            newSpot = s.to_dict()
            newSpot['wellReplicateIndex']=replicateIndex
            newSpot['wellLabel']=label
            newSpot['wellType']=type
            allSpots.append(newSpot)

        allSpotsCsv = codec.dictArrayToCsv(allSpots)
        await createArtifact("allSpots.csv", allSpotsCsv)
        archive = addToArchive(archive,'allspots.csv',allSpotsCsv)
        def removeOutliers(analyteSpots):
            results = analyteSpots
            if (len(analyteSpots) >= 3):
                outlierResultList = dixon_test( [s['intensity'] for s in analyteSpots])
                results = [ a for a in analyteSpots if a['intensity'] not in outlierResultList]
                removedSpots = [ b for b in analyteSpots if b['intensity'] in outlierResultList]
            return results
        def markOutliers(analyteSpots):
            results = analyteSpots
            if (len(analyteSpots) >= 3):
                outlierResultList = dixon_test( [s['intensity'] for s in analyteSpots])
                for a in analyteSpots:
                    if a['intensity'] in outlierResultList:
                        a['outlier'] = 1
                    else:
                        a['outlier'] = 0
            return results

        def averageAnalyteIntensities(analyteSpots):
            remainingMean = np.mean([a["intensity"] for a in analyteSpots])
            res =  [{**analyteSpots[0], "intensity":remainingMean}]
            return res

        analyteWellColumnKey = lambda s: f"{s['wellRow']}{s['wellColumn']}{s['analyte']}"

        allSpots = transformSpots(
            allSpots,
            markOutliers, #was removeOutliers
            analyteWellColumnKey)

        outlierList = []
        inlierList = []
        for a in allSpots:
            if 'outlier' in a and a['outlier'] == 1:
                   outlierList.append(a)
            else:
                inlierList.append(a)

        outlierSpotsCsv = codec.dictArrayToCsv(outlierList)
        await createArtifact("outlierSpots.csv", outlierSpotsCsv)
        archive = addToArchive(archive,"outlierSpots.csv",outlierSpotsCsv)
        processReport.append(f"Removed {len(outlierList)} spot intensities out of {len(allSpots)} total spots from the dataset based on Dixon's Q Test.")
        processReport.append("")

        initConcs = context['args']['initialConcentrations']
        dilf = int(context['args']['standardDilutionFactor'])
        allSpots = [addKnownConcentration(s, initConcs, dilf) for s in inlierList]
        allSpotsAverages = transformSpots(
            allSpots,
            averageAnalyteIntensities,
            analyteWellColumnKey)

        allSpotsCsvOutliersRemoved = codec.dictArrayToCsv(allSpots)
        await createArtifact("allSpots_outliers_removed.csv",allSpotsCsvOutliersRemoved )
        archive = addToArchive(archive,"allSpots_outliers_removed.csv", allSpotsCsvOutliersRemoved)
        def remove_keys(listOfDicts,listOfKeys):
            for k in listOfKeys:
                for d in listOfDicts:
                    del d[k]
            return listOfDicts

        allSpotsAveragesFiltered = remove_keys(allSpotsAverages,['row','column'])
        allSpotsAveragesCsv =  codec.dictArrayToCsv(allSpotsAveragesFiltered)
        await createArtifact("allSpots_outliers_removed_averaged.csv",allSpotsAveragesCsv )
        archive = addToArchive(archive,"allSpots_outliers_removed_averaged.csv",allSpotsAveragesCsv)
        def wellPropertyGetter(someSpots, f, analyte):
                    def g(col, row):
                        spts = (
                            f(s) for s in someSpots
                            if s['wellRow'] == row and s['wellColumn'] == str(col) and s['analyte'] == analyte #fit['name']
                        )
                        return next(spts, "")
                    return g

        #storing average curve inverse for the generation of the multiplate report
        analyteAverageInverseFitCurveDict = {}

        if hasStandards:   #generate one type of report for plates with standards
            # one best fit for each analyte
            someFits = [ calculateStandardCurve( allSpots, analyte)
                for analyte
                in listOfAnalytes
                #in context['args']['initialConcentrations'].keys()
            ]
            bestFits = []
            for b in someFits:
                if b != None:
                    bestFits.append(b)

            #collect some metadata so that users can understand what is happening

            fitAnalyteList = listOfAnalytes.copy()
            for f in bestFits:
                processReport.append(f"{f['name']}: {len(f['familyFunctionList'])}/100 sample curves generated and fit.")
                fitAnalyteList.remove(f['name'])
            processReport.append("")
            if len(fitAnalyteList) > 0:
                processReport.append(f"*** ATTENTION *** A standard curve could not be generated due to poor data quality for the following analytes: {fitAnalyteList}. Calculated concentrations will not be computed for for these analytes.")
            processReport.append("")
            for fit in bestFits:
                #collect inverse curves for use in multiplate report
                analyteAverageInverseFitCurveDict.update( {fit['name'] : fit['averageFitInverse'] })

                concentrationUnit = "pg/ml"
                try:
                    concentrationUnit = context['product']['initialConcentrationUnits'][0]
                except KeyError:
                    logger.info("No initial concentration unit field found in product.  Defaulting to pg/ml.")
                resultPlot, deltaPlot = createStandardPlot(fit,fit['fitType'], concentrationUnit, signalIntensityAlgorithm )
                fname = fit['name']+"_bestFit.jpg"
                dname = fit['name']+"_delta.jpg"
                await context['createAnalysisArtifact'](
                    "preview_"+fname,
                    codec.compressJpg(resultPlot,"maximum"))

                await context['createAnalysisArtifact'](
                    "preview_"+dname,
                    codec.compressJpg(deltaPlot,"maximum"))

                addToArchive(archive,fname,resultPlot)
                addToArchive(archive,dname,deltaPlot)

                LOQReport = createLOQReport(fit['LOQRegionsConcentrations'], concentrationUnit)
                standardReport = createStandardReport(allSpotsAverages, fit['name'], fit['averageFitInverse'], fit['LOQRegionsConcentrations'])

                unknownReport = createUnknownReportWithStandards(
                      allSpotsAverages,
                      fit['name'],
                      fit['averageFitInverse'],
                      concentrationUnit,
                      fit['LOQRegionsConcentrations'])

                plateMapConcentrations = createLabeledPlateMap(
                    wellPropertyGetter(allSpotsAverages,lambda w: fit['averageFitInverse'](w['intensity']),fit['name']))
                plateMapLabels = createLabeledPlateMap(
                    wellPropertyGetter(allSpotsAverages,lambda w: w['wellLabel'],fit['name']))
                plateMapIntensities = createLabeledPlateMap(
                    wellPropertyGetter(allSpotsAverages,lambda w: w['intensity'],fit['name']))

                multicsv = lambda *sections: utils.flatten(sections)
                section = lambda *rows: utils.flatten(rows)
                row = lambda *items: [items]
                fullReport = codec.arrayToCsv(
                    multicsv(
                        section(
                            row("Standard Report"),
                            row(*list(standardReport[0].keys())),
                            *[row(*list(r.values())) for r in standardReport],
                            row()),
                        section(
                            row("Unknown Report"),
                            row(*list(unknownReport[0].keys())),
                            *[row(*list(r.values())) for r in unknownReport],
                            row()),
                        section(
                            row("Plate Map Labels"),
                            *[row(*r) for r in plateMapLabels],
                            row()),
                        section(
                            row("Plate Map Intensities"),
                            *[row(*r) for r in plateMapIntensities],
                            row()),
                        section(
                            row("Plate Map Concentrations"),
                            *[row(*r) for r in plateMapConcentrations],
                            row()),
                        section(
                            row("Limits of Quantification"),
                            row(*list(LOQReport[0].keys())),
                            *[row(*list(r.values())) for r in LOQReport],
                        ) if len(LOQReport) > 0 else section(row("No valid limits of quantification were found."))
                    )
                )

                fname = f"summary_report_{fit['name']}.csv"
                await context['createAnalysisArtifact'](fname, fullReport)
                archive = addToArchive(archive,fname,fullReport)

                fname = f"heat_map_{fit['name']}.jpg"
                heatMap = createHeatMap(allSpots, fit['name'])
                heatMapCompressed = codec.compressJpg(codec.arrayToJpg(heatMap), 70)
                await context['createAnalysisArtifact'](
                    "preview_"+fname,
                    heatMapCompressed)
                    #codec.compressJpg(codec.arrayToJpg(heatMap), 30))
                archive = addToArchive(archive,fname,heatMapCompressed)

        else:  #create a different report for a plate with just unknowns and no standards
           for analyte in listOfAnalytes:
                unknownReport = createUnknownReportWithoutStandards(allSpotsAverages,analyte)
                plateMapLabels = createLabeledPlateMap(
                    wellPropertyGetter(allSpotsAverages,lambda w: w['wellLabel'],analyte))
                plateMapIntensities = createLabeledPlateMap(
                    wellPropertyGetter(allSpotsAverages,lambda w: w['intensity'],analyte))
                multicsv = lambda *sections: utils.flatten(sections)
                section = lambda *rows: utils.flatten(rows)
                row = lambda *items: [items]
                fullReport = codec.arrayToCsv(
                    multicsv(
                        section(
                            row("Unknown Report"),
                            row(*list(unknownReport[0].keys())),
                            *[row(*list(r.values())) for r in unknownReport],
                            row()),
                        section(
                            row("Plate Map Labels"),
                            *[row(*r) for r in plateMapLabels],
                            row()),
                        section(
                            row("Plate Map Intensities"),
                            *[row(*r) for r in plateMapIntensities],
                            row()),
                    )
                )
                fname = f"summary_report_{analyte}.csv"
                await context['createAnalysisArtifact'](fname, fullReport)
                archive = addToArchive(archive, fname,fullReport)
                fname = f"heat_map_{analyte}.jpg"
                heatMap = createHeatMap(allSpots, analyte)
                heatMapCompressed = codec.compressJpg(codec.arrayToJpg(heatMap), 30)
                await context['createAnalysisArtifact'](
                    "preview_"+fname, heatMapCompressed)
                archive = addToArchive(archive,fname,heatMapCompressed)
                #end unknown report without standards createion

        validationReportList = createValidationReport(allSpots,allSpotsAveragesFiltered,analyteAverageInverseFitCurveDict)
        validationReportCsv = codec.dictArrayToCsv(validationReportList)
        await createArtifact("validation_report.csv", validationReportCsv )
        archive = addToArchive(archive,'validateion_report.csv',validationReportCsv)
    except Exception as error:
        processReport.append(f"An unexpected error occurred: {error}")
    finally:

        processReport.append(f"pArrayFluoro Analysis ended at {datetime.utcnow()} UTC\n")
        processReportTxt = codec.listToText(processReport)

        await createArtifact("process_report.txt", processReportTxt )
        archive = addToArchive(archive,"process_report.txt",processReportTxt)

        await context['createAnalysisArtifact']('summary.zip', archive.getvalue() )
        logger.info("Analysis complete.")

def getImageDetails(imageDict,experimentWells):
    dataList = imageDict['metadata']
    resultList = []
    resultDict = {}
    for d in dataList:
        scanTime = d['time']
        fovSizeXUm = d['fovSizeXUm']
        fovSizeYUm = d['fovSizeYUm']
        wellName = d['imageName']
        spotList = d['spots']

        try:
            zStagePosUm = d['zStagePositionUm']
            xStagePosUm = d['xStagePositionUm']
            yStagePosUm = d['yStagePositionUm']
        except:
            logger.info("Could not retrieve stage data.  Defaulting values to 0.")
            zStagePosUm = 0
            xStagePosUm = 0
            yStagePosUm = 0

        spotDetailList = []
        for s in spotList:
            spotDetailList.append(SpotAcqDetails(**s))
        dc = ImageAcqDetails(time=scanTime,fovSizeXUm=fovSizeXUm,
                             fovSizeYUm=fovSizeYUm,imageName=wellName,
                             spots=spotDetailList,zStagePositionUm=zStagePosUm,
                             xStagePositionUm= xStagePosUm, yStagePositionUm=yStagePosUm)
        #resultList.append(dc)
        resultDict[wellName] = dc
    #create the list based on the order of wells in exeperimentWells
    for e in experimentWells:
        label = e['row']+e['column']
        resultList.append(resultDict[label])

    return resultList

def createSummaryReportZip(report):
    buff = io.BytesIO()
    with ZipFile(buff, mode='w') as zipf:
        for name, value in report.items():
            zipf.writestr(name, value)
    return buff.getvalue()

def createArchive():
    buff = io.BytesIO()
    return buff
def addToArchive(buff,name,report):
    with ZipFile(buff, mode='a') as zipf:
        zipf.writestr(name, report)
    return buff

def createHeatMap(spots, analyte):
    spots = [s for s in spots
        if s['analyte'] == analyte]

    #find the least intense spot value
    minIntensity = 10000000000
    for s in spots:
        if s['intensity']<minIntensity:
            minIntensity = s['intensity']

    def calculateMeanIntensityByWell(data):
        #calcuate the mean intensity of all the spots in a well
        data.sort(key=lambda x: x['well'])
        wellMeans = [{"well": key, "intensity": statistics.mean(item["intensity"] for item in group)}
            for key, group in itertools.groupby(data, key=lambda x: x['well'])]
        #reformat the result to { ('A','5'):intensity, ...}
        result = {
            ( s["well"][0],s["well"][1:]) : s["intensity"]
            for s in wellMeans
        }
        return result

    averageSpotIntensityDict = calculateMeanIntensityByWell(spots)

    intensityDict = {
        (s['wellRow'],s['wellColumn']):s['intensity']
        for s in spots
    }

    map = heatmapLib.createHeatMap(
        averageSpotIntensityDict,
        f"{analyte}",
        math.floor(max(spots, key=lambda s: s['intensity'])['intensity']),
        minIntensity,
        cv2.COLORMAP_JET)
    return map


def createValidationReport(allSpots, allSpotsAveragesFiltered, analyteAverageInverseFitCurveDict ):
    averageAnalyteIntensityDict = {}
    validationReportList = []
    for row in allSpotsAveragesFiltered:
        averageAnalyteIntensityDict.update({f"{row['well']}-{row['analyte']}":row['intensity'] })
    for row in allSpots:
        newRow = {}
        newRow.update({"well":row['well']})
        newRow.update({"well type":row['wellLabel']})

        if row['analyte'] not in ['BLANK','POS']:
           if row['wellType'] == 'standard':
                newRow.update({"standard concentration":row['knownConcentration']})
           else:
                newRow.update({"standard concentration":"null"})
           if row['analyte'] in analyteAverageInverseFitCurveDict:
                 invFunc = analyteAverageInverseFitCurveDict[row['analyte']]
                 calculatedConcentration = invFunc(averageAnalyteIntensityDict[ f"{row['well']}-{row['analyte']}"])
                 newRow.update({"calculated concentration":calculatedConcentration})
           else:
                 newRow.update({"calculated concentration":"null"})
        else:
            newRow.update({"standard concentration":"null"})
            newRow.update({"calculated concentration":"null"})

        newRow.update({"analyte":row['analyte']})
        newRow.update({"replicate mean intensity":averageAnalyteIntensityDict[ f"{row['well']}-{row['analyte']}"]})
        newRow.update({"signal adjusted intensity":row['intensity']})
        validationReportList.append(newRow)
    return validationReportList
def isValid(value, ranges):
        result = False
        for r in ranges:
            if value >= r[0] and value <= r[1]:
                result = True
                break
        return result
def createStandardReport(allSpots, analyte, averageInverseFunction, LOQRegions):

    labels = set([p['wellLabel'] for p in allSpots
        if p['wellType'] == "standard"
        or p['wellType'] == "blank"])
    # big default number ensures blanks sort last
    labels = sorted(labels,
        key=lambda l: 1000 if l == 'blank' else int(l.replace("stnd","")))

    rows = []
    for l in labels:
        spots = [s for s in allSpots
            if s["wellLabel"] == l
            and s['analyte'] == analyte]

        if len(spots) != 2:
            logger.info(f'non-two spots in CSR {spots}')

        c = spots[0]['knownConcentration']

        isBlank = spots[0]['wellType']=='blank'
        meanSpotReplicateConcentration =  averageInverseFunction(np.mean( [ s['intensity'] for s in spots ]))

        row = {
            "wellLabel": l,
            "concentration": c,
            **{
                f"replicate_{s['wellReplicateIndex']}_intensity": s['intensity']
                for s in spots
            },
            "mean replicate intensity": np.mean( [ s['intensity'] for s in spots ] ),
            "mean replicate calculated concentration": meanSpotReplicateConcentration,
            "percent concentration difference": "blank not calculated" if isBlank \
                else float("{:.2f}".format(abs(c - meanSpotReplicateConcentration) / c * 100) ),
            "within limits of quantification": "Y" if isValid(meanSpotReplicateConcentration,LOQRegions) else "N"
        }
        rows.append(row)
    return rows

def createUnknownReportWithoutStandards(allSpots,analyte):
    rows = []
    wellLabels = sorted(set([
        p['wellLabel']
        for p in allSpots
    ]))
    for wellLabel in wellLabels:
        spots = [s for s in allSpots
             if s["wellLabel"] == wellLabel
             and s['analyte'] == analyte]
        row = {
            "wellLabel": wellLabel,
            **{
                f"replicate{s['wellReplicateIndex']} intensity": s['intensity']
                for s in spots
            },
        }
        rows.append(row)
    return rows

def createUnknownReportWithStandards(allSpots, analyte, averageFitInverse, concentrationUnit, LOQRegions):

    wellLabels = sorted(set([
        p['wellLabel']
        for p in allSpots
        if p['wellType'] == "unknown"
    ]))

    rows = []
    for wellLabel in wellLabels:
        spots = [s for s in allSpots
            if s["wellLabel"] == wellLabel
            and s['analyte'] == analyte]

        concentrations = [averageFitInverse(s['intensity']) for s in spots]
        # self-equality ensures not NaN
        stddevconc = None if any(c != c for c in concentrations) or len(concentrations)==1 else stdev(concentrations)
        row = {
            "wellLabel": wellLabel,
            **{
                f"rep{s['wellReplicateIndex']} intensity": s['intensity']
                for s in spots
            },
            **{
                f"rep{s['wellReplicateIndex']} concentration ({concentrationUnit})":
                    averageFitInverse(s['intensity'])
                for s in spots
            },
            f"mean of rep concentration ({concentrationUnit})": mean(concentrations),
            f"sdev of replicate concentration ({concentrationUnit})": stddevconc,
            "within limits of quantification": "Y" if isValid(mean(concentrations),LOQRegions) else "N"
        }
        rows.append(row)

    if len(rows) == 0:
        rows.append({"No unknowns present.":""})
    return rows

def createLOQReport(LOQRegions, units):
    rows = []
    for r in LOQRegions:
        row = { "LLOQ ("+units+")": r[0],
                "ULOQ ("+units+")": r[1] }
        rows.append(row)
    return rows

def createLabeledPlateMap(getLabel):

    cols = range(1,13)
    rows = ["A","B","C","D","E","F","G","H"]

    plateMapLabels = [
        [
            row
        ]+[
            getLabel(col, row)
            for col in cols
        ]
        for row in rows
    ]
    # add col headers
    plateMapLabels.insert(0, [""]+list(cols))
    return plateMapLabels


def createStandardPlot(bestFit, fitType, concentrationUnits, signalIntensityAlgorithm ):

    regionsConc = bestFit['LOQRegionsConcentrations']
    regionsIntensities = bestFit['LOQRegionsIntensities']
    qRangesString = ""
    for r in regionsConc:
       lowEnd = '{0:.3f}'.format(r[0])
       hiEnd = '{0:.2f}'.format(r[1])
       qRangesString= qRangesString+lowEnd+" to "+hiEnd+"\n"

    blankIntensity = mean([p[1] for p in bestFit['blankxys']])

    plotMaxYValue = 3*max(bestFit['standardxys'], key=lambda p: p[1])[1]
    plotMinXValue = 0.1*min(bestFit['standardxys'], key=lambda p: p[0])[0]

    plotTitle = bestFit['name'] + ' (fit type:'+str(fitType)+'PL)' + ' ' + signalIntensityAlgorithm

    deltaTitle = "Percent difference between curves for " + bestFit['name']

    deltaPlot = plt.plot([
        plt.Title(deltaTitle, fontsize=20),
        plt.Height(1000), plt.Width(1000),
        plt.XScaleLog(10),
        plt.Background("whitesmoke"),
        plt.XMin(0.75*min(bestFit['standardxys'], key=lambda p: p[1])[1]),
        plt.XMax(3*max(bestFit['standardxys'], key=lambda p: p[1])[1]),
        plt.YMin(.00001),
        plt.YMax(50),
        plt.Function(bestFit['upperPercentDifference'], color="green"),
        plt.Function(bestFit['lowerPercentDifference'], color="blue"),
        plt.YLabel("% Difference",fontsize=18),
        plt.XLabel("Intensity",fontsize=18),
        plt.Function(
            lambda x: 20,
            color="gray",
            linestyle="dashed",
        ),
        plt.Function(
             lambda x: bestFit['lowConcentrationAverageIntensity'],
             color="red",
             linestyle="dashed",
             dependentaxis="x"
         ),
        plt.Function(
             lambda x: bestFit['hiConcentrationAverageIntensity'],
             color="red",
             linestyle="dashed",
             dependentaxis="x"
         ),
        *[
             plt.ShadedXRegion(
                 p[0],
                 p[1],
                 "green",
                 0.2
             ) for p in regionsIntensities
         ]
    ])

    resultPlot = plt.plot([
        plt.Title(plotTitle, fontsize=20),
        plt.Height(1000), plt.Width(1000),
        plt.XScaleLog(10), plt.YScaleLog(10),
        plt.Background("whitesmoke"),
        plt.XMin(0.1*min(bestFit['standardxys'], key=lambda p: p[0])[0]),
        plt.XMax(10*max(bestFit['standardxys'], key=lambda p: p[0])[0]),
        plt.YMin(0.75*min(bestFit['standardxys'], key=lambda p: p[1])[1]),
        plt.YMax(3*max(bestFit['standardxys'], key=lambda p: p[1])[1]),
        plt.Text(f"\nValid quantification ranges ({concentrationUnits}):\n{qRangesString}",
                  plotMinXValue*3,
                  plotMaxYValue,
                  #plotMaxYValue - 10*10**(math.log10(plotMaxYValue/5)),
                  horizontalalignment='left',
                  verticalalignment='top',
                  fontsize=12),
        plt.Function(bestFit['upperFit'], color="green"),
        plt.Function(bestFit['averageFit'], color="red"),
        plt.Function(bestFit['lowerFit'], color="blue"),
        # shaded LOQ regions
        *[
                plt.ShadedXRegion(
                    p[0],
                    p[1],
                    "green",
                    0.2
                ) for p in regionsConc
        ],
        # 100 curves
        *[
            plt.Function(
                p,
                color="gray",
                alpha=.1)
                for p in bestFit['familyFunctionList']
        ],
        # standard intensity points
        *[
            plt.Point(Point(p[0],p[1]),color="black",marker="+",markersize=15)
            for p in bestFit['standardxys']
        ],
        # LLOQ line
        *[
        plt.YLabel("Intensity",fontsize=18),
        plt.XLabel("Concentration ("+concentrationUnits+")",fontsize=18),
        # blank intensity line
        plt.Function(
            lambda x: blankIntensity, 
            color="gray", 
            linestyle="dashed",
        ),
        plt.Text(
            "Blank Intensity", 
            max(bestFit['standardxys'], key=lambda p: p[0])[0],
            blankIntensity-10,
            horizontalalignment='right'
        )
        ]
    ])
    return resultPlot, deltaPlot

def selectLogisticFitType(fitInputs):

    fitValues5, sumOfSquaresResidual5 = fit5(*fitInputs)
    fitValues4, sumOfSquaresResidual4 = fit4(*fitInputs)

    numberOfPoints = len(fitInputs[0])
    desiredConfidence = 0.9

    #Using just the best 2 out of 3 standard points and blank...
    #Determine which model fits the data better, 4PL vs. 5PL.
    fTest = ( (sumOfSquaresResidual4 - sumOfSquaresResidual5) / sumOfSquaresResidual5 ) * (numberOfPoints)
    fCritical = f.ppf(desiredConfidence,1,numberOfPoints-5)

    fitType = 4
    if (fTest>fCritical):
        logger.info('*** Choosing 5PL!')
        fitType = 5
    else:
        logger.info('*** Choosing 4PL')

    return fitType
    
def calculateStandardCurve(
    allSpots, 
    analyte
):

    try:

        blankIntensities = [
            s['intensity'] for s in allSpots
            if s['wellType'] == 'blank'
            and s['analyte'] == analyte
        ]

        standardSpots = [
            s for s in allSpots
            if s['wellType'] == 'standard'
            and s['analyte'] == analyte
        ]

        standardLabels = list(sorted(
            set([s['wellLabel'] for s in standardSpots]),
            key=lambda l: int(l.replace("stnd",""))
        ))

        def spotsWithStandard(spots, stdLabel):
            return [s for s in spots if s['wellLabel'] == stdLabel]
        spotsGroupedByWellLabel = [spotsWithStandard(standardSpots, lbl)
            for lbl in standardLabels]

        standardxys = [
            (s['knownConcentration'], s['intensity'])
            for i, spots in enumerate(spotsGroupedByWellLabel)
            for s in spots
        ]

        logger.info(f'Starting Best Fit Function for analyte: {analyte} ')
        logger.info(f'Standard x,ys {standardxys} ')

        blankxys = [(1*10**-10, y) for y in blankIntensities] #was 2*10**-100
        fitInputs = list(zip(*(standardxys + blankxys)))
        fitxys = standardxys + blankxys

        fitType = selectLogisticFitType(fitInputs)

        #generate 100 sample curves and average the parameters to determine the best fit
        #marshal the standardxys data to be used for random intensity picking
        #concentrationIntensityDict is of the form:  { 1000: [42532,41399,43131,41323],500: [28023,28352,29032,28352],...)
        concentrationIntensityDict = { dictConcentration:
                                       [intensity for concentration,intensity in fitxys if concentration == dictConcentration]
                                       for dictConcentration in
                                       [concentration for concentration,intensity in fitxys]
                                       }

        logger.info(f'Step 2: Organize the data for random sampling.  For analyte: {analyte} concentration-intensity dict: {concentrationIntensityDict}')

        def generateFamilyCurves(concentrationDict, fitType):
            xVals = [ float(k) for k in concentrationDict.keys() ]
            yVals = [ random.choice(concentrationDict[k]) for k in concentrationDict.keys()]
            try:
                if (fitType == 4):
                    fitValues4PL, res4 = fit4(xVals,yVals)
                    return lambda x: logistic4(x,*fitValues4PL)
                else:
                    fitValues5PL, res5 = fit5(xVals,yVals)
                    return lambda x: logistic5(x,*fitValues5PL)
            except Exception as e:
                logger.info("Could not fit a curve in generateFamilyCurves.")
                return None

        #this list contains ~100 curve fit params
        familyFunctionList = []
        for x in range(0,100):
            func=generateFamilyCurves(concentrationIntensityDict,fitType)
            if func != None:
                familyFunctionList.append(func)

        numberOfCurves = len(familyFunctionList)
        logger.info(f'For analyte: {analyte} there were {numberOfCurves} curves')

        #for each of the 100 curves, calculate the intensity values at each standard
        concentrations = list(concentrationIntensityDict.keys())
        concentrations.sort()

        #for bracketing loq calcluations
        concentrationsList = concentrations[1:]
        concentrationBrackets = [(concentrationsList[i], concentrationsList[i+1]) for i in range(len(concentrationsList)-1)]
        logger.info(f'Concentration brackets: {concentrationBrackets} ')

        concentrationCurvesPointsDict = {
            c: list(sorted(m(c) for m in familyFunctionList))
            for c in concentrations }
        confidenceIndex = lambda xs: math.ceil(len(xs)*0.025)
        concLowAvgUppValuesDict = {
            k: (vs[confidenceIndex(vs)], np.mean(vs), vs[-confidenceIndex(vs)])
            for k, vs in concentrationCurvesPointsDict.items() }
        lowerValueDict = {k:vs[0] for k,vs in concLowAvgUppValuesDict.items()}
        averageValueDict = {k:vs[1] for k,vs in concLowAvgUppValuesDict.items()}
        upperValueDict = {k:vs[2] for k,vs in concLowAvgUppValuesDict.items()}

        logger.info(f'upper value dict: {upperValueDict}')
        logger.info(f'average value dict: {averageValueDict}')
        logger.info(f'lower value dict: {lowerValueDict}')

        logger.info(f'Step 5: fit the upper, lower, and average curves.')
        if (fitType == 4):
            fit = fit4
            fitFunction = logistic4
            fitInvFunction = logistic4Inverse
        else:
            fit = fit5
            fitFunction = logistic5
            fitInvFunction = logistic5Inverse

        upperFitValues,resid = fit(list(upperValueDict.keys()),list(upperValueDict.values()))
        averageFitValues,resid = fit(list(averageValueDict.keys()),list(averageValueDict.values()))
        lowerFitValues,resid = fit(list(lowerValueDict.keys()),list(lowerValueDict.values()))
        upperFit = lambda x: fitFunction(x, *upperFitValues)
        averageFit = lambda x: fitFunction(x, *averageFitValues)
        lowerFit = lambda x: fitFunction(x, *lowerFitValues)
        upperFitInv = lambda x: fitInvFunction(x, *upperFitValues)
        averageFitInv = lambda x: fitInvFunction(x, *averageFitValues)
        lowerFitInv = lambda x: fitInvFunction(x, *lowerFitValues)

        upperPercentDiff = lambda x: ( ( fitInvFunction(x, *averageFitValues) - fitInvFunction(x,*upperFitValues) ) / fitInvFunction(x,*averageFitValues) ) * 100
        lowerPercentDiff = lambda x: ( ( fitInvFunction(x, *lowerFitValues) - fitInvFunction(x,*averageFitValues) ) / fitInvFunction(x,*averageFitValues) ) * 100

        logger.info(f"Calculating LOQ ranges for analyte is: {analyte}")
        low = concentrationsList[0]
        hi = concentrationsList[-1]

        try:
            logger.info("Calculating upper intervals.")
            upperIntervals = getValidRanges(low,hi,upperPercentDiff,upperFit,averageFit,"upper")
            logger.info("Calculating lower intervals.")
            lowerIntervals = getValidRanges(low,hi,lowerPercentDiff,lowerFit,averageFit,"lower")
            logger.info(f"Lower intervals: {lowerIntervals}")
            logger.info(f"Upper intervals: {upperIntervals}")

            def convertIntensitiesToConcentrations(regions, func):
                res = []
                for r in regions:
                    i = []
                    i.append(func(r[0]))
                    i.append(func(r[1]))
                    res.append(i)
                return res

            logger.info("Finding overlaps...")
            consolidatedList = findOverlaps(lowerIntervals, upperIntervals)
            concRegions = convertIntensitiesToConcentrations(consolidatedList, averageFitInv)
            logger.info(f'Consolidated list (intensities): {consolidatedList}')
            logger.info(f'Consolidated list (concentrations): {concRegions}')
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            logger.info(message)

        resultDict = { "name":analyte,
                       "averageFit":averageFit,
                       "averageFitInverse":averageFitInv,
                       "standardxys":standardxys,
                       "blankxys":blankxys,
                       "fitType":fitType,
                       "upperFit":upperFit,
                       "lowerFit":lowerFit,
                       "familyFunctionList":familyFunctionList,
                       "LOQRegionsConcentrations":concRegions,
                       "LOQRegionsIntensities":consolidatedList,
                       "lowerPercentDifference":lowerPercentDiff,
                       "upperPercentDifference":upperPercentDiff,
                       "lowConcentrationAverageIntensity":averageFit(low),
                       "hiConcentrationAverageIntensity":averageFit(hi)}

        logger.info(f"Completed calculateStandardCurve curve for {analyte}")
        return resultDict
    except:
        logger.info(f"WARNING: Could not generate a standard curve for analyte {analyte}.")
        return None

#   given a well, returns the spots and their intensities
async def getIntensities(well, featurePoints, createArtifact):

    im = well['image'].copy()

    pxlFeaturePts = pointsToPixelSpace(featurePoints, im)
    posCtlPoint = next(p for p in pxlFeaturePts 
        if p.dict.get('analyte', None) == "POS")
    posCtlNeighborPt = next(p for p in pxlFeaturePts
        if p.dict.get('row', None) == 1
        and p.dict.get('column', None) == 2)
    halfGridUnit = (posCtlNeighborPt.x - posCtlPoint.x)//2
    
    imgspots = imageLib.findSpots(im, 40, 100, 500)
    spotNearestPosControl = min(
        imgspots, 
        key=lambda s: pow(s['x']-posCtlPoint.x, 2)+pow(s['y']-posCtlPoint.y, 2))
    microArrayShift = Point(
        spotNearestPosControl['x']-posCtlPoint.x,
        spotNearestPosControl['y']-posCtlPoint.y
    )
    spotPts = [
        (p+microArrayShift).toDict() for p in pxlFeaturePts
        if p.dict.get("type", None) == "spot"
    ]
    
    def getSpotIntensity(spot):
        roi = im[
            spot['y']-halfGridUnit:spot['y']+halfGridUnit,
            spot['x']-halfGridUnit:spot['x']+halfGridUnit
        ]
        mean = np.mean(roi)
        signalMean = np.mean(roi, where=roi>mean)
        backgroundMean = np.mean(roi, where=roi<=mean)
        res = signalMean - backgroundMean

        return res
    
    spotPts = [
        {**s, "intensity": getSpotIntensity(s)}
        for s in spotPts
    ]

    return spotPts
