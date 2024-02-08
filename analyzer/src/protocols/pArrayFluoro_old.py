import sys

from matplotlib import pyplot as plt

sys.path.insert(0, './common')
import utils
from functools import reduce
import asyncio
import imageLib
import cv2
import itertools
import operator
import numpy as np
import arraySpotLib
import pandas as pd
import random
import curveFitter
from matplotlib.ticker import ScalarFormatter, FuncFormatter
import warnings
import log
import artifactCodec
import collections

logger=log.getLogger('analyzer.src.protocols.pArrayFluoro_old')
warnings.filterwarnings("ignore")

pd.set_option('display.max_rows',500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

argSchema = {
    "type": "object"
}

# docker-compose build
# docker run --mount type=bind,src=c:/Users/jpeck/source/Phoenix/test-data,dst=/test-data phoenix_analyzer --analysis ./test-data/run3/analysis.json

codec = artifactCodec.ArtifactCodec()

async def execute(context):

    logger.info("Executing pArrayFluoro Analysis")

    #start marshalling the data from the product and scan databases
    #hasStandards = args['experimentConfiguration']['hasStandards']
    # analysisWells = context['args']['experimentConfiguration']['wells']
    # productWells = context['args']['productConfiguration']['wells']
    # spotPoints = context['args']['productConfiguration']['spots']

    analyteDict =  { (spot["row"],spot["column"]):spot["analyte"] for spot in spotPoints if spot["analyte"] != "BLANK" }
    uniqueAnalytes = list(set(analyteDict.values()))
    uniqueAnalytes.remove('POS')
    #uniqueAnalytes.remove('BLANK')

    analysisWellsDict ={ (well['row']+well['column']).upper():well for well in analysisWells }
    productWellsDict ={ (well['row']+well['column']).upper():well for well in productWells }
    print("\nAll Analysis Wells Dict: ",analysisWellsDict)

    standardAnalysisWellsDict ={ (well['row']+well['column']).upper():well for well in analysisWells if well["type"] == "standard" }
    unknownAnalysisWellsDict ={ (well['row']+well['column']).upper():well for well in analysisWells if well["type"] == "unknown" }

    hasStandards =  bool(standardAnalysisWellsDict)
    hasUnknowns =   bool(unknownAnalysisWellsDict)

    logger.info("Has standards? " + str(hasStandards))
    logger.info("Has unknowns? " + str(hasUnknowns))

    logger.info("Standard Analysis Wells Dict: "+str(standardAnalysisWellsDict))
    logger.info("Unknown Analysis Wells Dict: "+str(unknownAnalysisWellsDict))

    #generate a list of known concentrations for reporting
    #unique, reverse sorted set of concentrations
    def uniqueSort(aList):
        return list(np.sort(np.unique(np.array(aList))))  #to reverse: [::-1])

    #stdConcentrationList = uniqueSort([ well['knownConcentration'] for well in analysisWells])[::-1]
    stdConcentrationList = uniqueSort([ well['knownConcentration'] for well in analysisWells if well['type']=="standard" ])[::-1]
    print("\nConcentration List: ",stdConcentrationList)

    replicateGroupList = uniqueSort([ well['replicateGroup'] for well in analysisWells])
    replicateIdList = uniqueSort([ well['replicateId'] for well in analysisWells])

    print("\nReplicate Group List: ",replicateGroupList)
    print("\nReplicate ID List: ",replicateIdList)

    #get scan results metadata
    metaData = await context['getScanArtifact']('scanResultsMetadata.json')
    scanMetadata = codec.jsonToDict(metaData)
    #scanMetadata = await scanArtifactHlpr.getJson("scanResultsMetadata.json");

    #make a nice scanData dict
    scanWells = scanMetadata['wells']
    positionList = scanMetadata['positions']
    scanResolution = scanMetadata["resolutionX"]

    #computing some values using product and scan data
    spotDistance = int(context['args']['productConfiguration']['spotXDistance'])/scanResolution
    spotRadius = int(int(context['args']['productConfiguration']['spotSize'])/scanResolution/2)

    print("\nHas standards? ",hasStandards)
    print("\nScan resolution",scanResolution)
    print("\nSpot radius",spotRadius)
    print("\nSpot distance",spotDistance)

    firstFeatureDict = arraySpotLib.calculateFirstFeatureCoordsPixels(scanWells,productWells,scanResolution)
    print("\nFirst feature dict:",firstFeatureDict)

    #produce an list of indexes to analyze based on the scan metadata and the user designed experiment
    framesToAnalyzeList = []
    for k in analysisWellsDict.keys():
        if k in positionList:
            framesToAnalyzeList.append( positionList.index(k) )
    print("\nFrame indicies to analyze: ",framesToAnalyzeList)

    async def processFrame(frame, index):
        #detection parameters calculated based on default spot size
        minimumControlSpotRadius = int(spotRadius*.5)
        thresholdFactor = 3
        backgroundRadiusPixels = int(spotRadius * 1.5)
        backgroundThickness = 3
        windowLength = spotRadius*3
        maxDetectionDistance = int(spotRadius*.65)  # was .5
        blockPoints = analyteDict.keys()
        wellAddress = positionList[index-1]
        targetPoint = firstFeatureDict[wellAddress]

        # create the initial data dictionary
        spotsInit = [ {"spotAddress": s, "position": wellAddress, "frame":index} for s in blockPoints ]

        # start with first feature points from gal file (or 0,0) and then detect the actual control spot coordinates on the image
        controlPoint = imageLib.findCircleNearestPoint(frame, minimumControlSpotRadius, thresholdFactor, targetPoint)

        spots = utils.chain([
            utils.cmap(lambda c: {**c, "estimatedSpot": arraySpotLib.generateSpotPoint(controlPoint,c["spotAddress"],spotDistance)}),
            utils.cmap(lambda c: {**c, "detectedSpot": arraySpotLib.findSpotPoint(frame,c["estimatedSpot"],windowLength,maxDetectionDistance,thresholdFactor)}),
            utils.cmap(lambda c: {**c, "spotMean":arraySpotLib.getMeanIntensityOfCircle(frame, c["detectedSpot"], spotRadius)}),
            utils.cmap(lambda c: {**c, "backgroundMedian":arraySpotLib.getMedianIntensityOfBackground(frame, c["detectedSpot"], backgroundRadiusPixels, backgroundThickness)}),
            utils.cmap(lambda c: {**c, "signal": c["spotMean"] - c["backgroundMedian"] }),
            utils.cmap(lambda c: {**c, "analyte": analyteDict[c["spotAddress"]]}),
            utils.cmap(lambda c: {**c, "wellType": analysisWellsDict[c["position"]]["type"].upper()}),
            utils.cmap(lambda c: {**c, "label": analysisWellsDict[c["position"]]["label"]}),
            utils.cmap(lambda c: {**c, "replicateGroup": analysisWellsDict[c["position"]]["replicateGroup"] if c["position"] in analysisWellsDict.keys() else None  }),
            utils.cmap(lambda c: {**c, "replicateId": analysisWellsDict[c["position"]]["replicateId"] if c["position"] in analysisWellsDict.keys() else ''  }),
            utils.cmap(lambda c: {**c, "knownConcentration": analysisWellsDict[c["position"]]["knownConcentration"] if c["position"] in analysisWellsDict.keys() else ''  })
        ])(spotsInit)

        #intermediate annotated image used for debugging
        layeredImg = arraySpotLib.annotatePoints(frame,
                                      [s["detectedSpot"] for s in spots],
                                      wellAddress,thresholdFactor, spotRadius, backgroundRadiusPixels, backgroundThickness)
        validationImageFileName = "validation_"+str(index)+".jpg"
        logger.info("Saving validation image:"+validationImageFileName)
        await createAnalysisArtifact(validationImageFileName, codec.arrayToJpg(layeredImg))
        return spots

    stack = codec.tiffStackToArray(await context['getScanArtifact']('pArrayFluoro.tif'))

    #save the spots artifact
    #if i in framesToAnalyzeList
    #TODO ask Ian about this...framesToAnalyzeList syntax
    spots = utils.flatten([await processFrame(f, i+1)
                           for i,f in enumerate(stack) if i in framesToAnalyzeList ] )

    async def computeStatistics(spots):
        sortedByColumn = sorted(spots, key=lambda x: int(x["position"][1:]))   #sort by column coordinate in position field  e.g. B12 -> 12
        sortedByRow = sorted(sortedByColumn, key=lambda x: x["position"][:1])       #sort by row coordinate in position field e.g. B12 - > B
        df = pd.DataFrame(sortedByRow)

        def replaceOutlier( signalList ):
            if len(signalList)>=3:
                meanValue = np.mean(signalList)
                #sort the signals based on each items distance from the mean of the set.  Farthest distance first.
                sortedSignals = list(sorted(signalList, key=lambda s: abs(meanValue - s), reverse=True))
                #replace the entry with the furthest distance with the mean of the remaining values
                signalList[signalList.index(sortedSignals[0])] = np.mean(sortedSignals[1:])
            return signalList

        #This fills up the adjusted signal dict with the desired data (signals with outliers removed)
        #and then adds it back to the dataframe
        gb = df.groupby(['position','analyte'])['signal'].groups
        adjustedSignalsDict = {sigs[0]:replaceOutlier(df["signal"][sigs].tolist()) for _, sigs in gb.items()}

        # sort the keys by the original ordered index to get the correct order and create a list.
        # add it back to the dataframe
        adjustedSignalsList = [adjustedSignalsDict[key] for key in sorted(adjustedSignalsDict.keys())]
        df['adjustedSignal'] = utils.flatten(adjustedSignalsList)

        # create a column of grouped means
        df['wellReplicateMean'] = df.groupby(['position','analyte'])['adjustedSignal'].transform(np.mean)

        if (hasStandards):
            #boolean indexing to reduce the data we are looking at here
            #subset =  df[(df['wellType']!='unknown')&(df['analyte']!='pos')].filter(items=["position","wellType","analyte","knownConcentration","adjustedSignal"])
            subset =  df[(df['wellType'] == 'STANDARD')].filter(items=["position","wellType","analyte","knownConcentration","adjustedSignal"])

        #print("Subset should only contain standards: \n",subset.to_string())

        workingArr = subset.to_numpy()

        def aggregateAnalytes(acc,row):
            value = row[4]
            conc = row[3]
            anlt = row[2]
            if (anlt not in acc):
                acc[anlt]={}
            if (conc not in acc[anlt]):
                acc[anlt][conc] = []
            acc[anlt][conc].append(value)
            return acc

        #desired structure:  {"anlt1":{ 1000: [s1,2,3,4,5...], 250: [s2,2,3,4,5...], 12 ] } }
        analyteConcentrationIntensityMap = reduce(aggregateAnalytes,workingArr,{})
        print("\nAnalyte Concentration Intensity Map:\n",analyteConcentrationIntensityMap)
        def calculateParameters(concentrationDict):
            xVals = [ float(k) for k in concentrationDict.keys()]
            yVals = [ random.choice(concentrationDict[k]) for  k in concentrationDict.keys()]
            (a,b,c,d) = curveFitter.fit(xVals,yVals)
            return (a,b,c,d)

        parameterResultDict = { anlt: [ calculateParameters(analyteConcentrationIntensityMap[anlt])
                                        for x in range(0,100) ] for anlt in analyteConcentrationIntensityMap.keys() }
        analyteParamDict = { k: list(map(np.mean,zip(*parameterResultDict[k])))
                                        for k in parameterResultDict.keys() }

        print("Result dict: ",analyteParamDict)

        #adjustedSignals = subset.groupby(['analyte','knownConcentration'])["adjustedSignal"]

        #for each analyte:
        print("\nUnique analytes: ",uniqueAnalytes)
        analyteAvgCurveDict = {}

        # generate avg curve data for each analyte - the red line in each plot
        for uniqueAnalyte in uniqueAnalytes:
            xAvgs = np.logspace(start=-4, stop=4, num = 100,base=10.0,endpoint=True)
            aMean = analyteParamDict.get(uniqueAnalyte)[0]
            bMean = analyteParamDict.get(uniqueAnalyte)[1]
            cMean = analyteParamDict.get(uniqueAnalyte)[2]
            dMean = analyteParamDict.get(uniqueAnalyte)[3]
            yAvgs = [ curveFitter.logistic4(x,
                                            aMean,
                                            bMean,
                                            cMean,
                                            dMean) for x in xAvgs ]

            #print("Params for analyte ",uniqueAnalyte,": ",aMean,bMean,cMean,dMean)
            analyteAvgCurveDict.update( {uniqueAnalyte:[xAvgs,yAvgs]})
            #print("Average params:",analyteAvgCurveDict)

        #back calculate concentrations based on curve results
        for uniqueAnalyte in uniqueAnalytes:
            analyteIndex = df["analyte"]==uniqueAnalyte
            replicates = df.loc[analyteIndex,"wellReplicateMean"]
            # back calculate the concentrations using the wellReplicate means and average fit params
            params = analyteParamDict.get(uniqueAnalyte);
            df.loc[analyteIndex,"calculatedConcentration"] = curveFitter.logistic4Inverse(replicates,
                                                                                          params[0],
                                                                                          params[1],
                                                                                          params[2],
                                                                                          params[3])

        # apply to all values
        def percentDifference(x,y):
            return ( abs(x-y) / ((x+y)/2) ) * 100

        if ( type(df['knownConcentration']) == int or type(df['knownConcentration'])==float ):
            df['concentrationPercentDifference'] = percentDifference( df['knownConcentration'], df['calculatedConcentration'])
        else:
            df['concentrationPercentDifference'] = ''

        fig, ax = plt.subplots(len(uniqueAnalytes)+1)
        #fig, ax = plt.subplots(nrows=4, ncols=4)
        ax[0].loglog(xAvgs,yAvgs,"-")
        ax[0].set_title('set of anlt1 avg curves')

        plotIndex=1

        #frmt = ScalarFormatter()
        frmt = FuncFormatter(lambda y, _: '{:.16g}'.format(y))
        for uniqueAnalyte in uniqueAnalytes:
            #ax[plotIndex].loglog(xAvgs,yAvgs,"r-")
            # retrieve the stored average curves for each analyte
            ax[plotIndex].loglog(analyteAvgCurveDict.get(uniqueAnalyte)[0],
                                 analyteAvgCurveDict.get(uniqueAnalyte)[1],
                                 "r-")
            plotTitle = "Standard Curve for " + uniqueAnalyte
            ax[plotIndex].set_title(plotTitle)
            ax[plotIndex].get_xaxis().set_major_formatter(frmt)
            ax[plotIndex].set_xlabel('Concentration (pg/ml)')
            ax[plotIndex].set_ylabel('Intensity')
            for p in subset.values:
                if (p[2]==uniqueAnalyte):
                    ax[plotIndex].loglog(p[3],p[4],'k_')
                    #ax[plotIndex].loglog(xAvgs,yAvgs,"r-")

            xmin,xmax = ax[plotIndex].get_xlim()
            ymin,ymax = ax[plotIndex].get_ylim()
            ax[plotIndex].set_xlim([0.001,xmax])
            ax[plotIndex].set_ylim([0,ymax+500])
            plotIndex=plotIndex+1

        plt.subplots_adjust(hspace=.8)
        fig.set_size_inches(5,72)

        await context['createAnalysisArtifact']("standardCurves.png", codec.figToPng(fig))
        await context['createAnalysisArtifact']("results.csv",
                                     codec.dictArrayToCsv(df.to_dict('records'))
                                     )

        #await analysisArtifactHlpr.storeFig("standardCurves.png","",fig)
        #await analysisArtifactHlpr.storeCsv("results.csv","",df.to_dict('records'))

        #print(df)
        return df

    #sanity check
    print("\nSpots",spots[0:3])

    stats = await computeStatistics(spots)

    async def report(stats):
        #for each unique analyte
        #for each well get the desired value and add it to the list

        #unknown data
        unkDf =  stats[ (stats['wellType']=='UNKNOWN')&(stats['analyte']=='ANLT1')].filter(items=["position","analyte","label","calculatedConcentration","wellReplicateMean","replicateGroup","replicateId"])
        #logger.info("\nUnknown dataframe subset:\n"+unkDf.to_string())
        workingUnkArr = unkDf.to_numpy()
        #sort the input array by group number
        logger.info("Working unknown array:"+str(workingUnkArr))

        def aggregateUnknowns(acc,row):
            label = row[2]
            intensity = row[4]
            concentration = row[3]
            grp = row[5]
            if (label not in acc):
                acc[label] = {"intensities":[],"concentrations":[]}
            if (intensity not in acc[label]["intensities"]):
                acc[label]["intensities"].append(intensity)
            if (concentration not in acc[label]["concentrations"]):
                acc[label]["concentrations"].append(concentration)
            return acc

        unkTableMap = reduce(aggregateUnknowns,workingUnkArr,{})
        logger.info("Unknown table map after reduce: "+str(unkTableMap))

        unkTableMap = { k: { **unkTableMap[k],
                            "mean":np.mean(unkTableMap[k]["concentrations"]),
                            "sdev":np.std(unkTableMap[k]["concentrations"])
                            }  for k in unkTableMap.keys() }
        logger.info("Updated unknown table map after reduce: "+str(unkTableMap))

        # example data: {'unk1': {'intensities': [65864.326171875, 32343.22265625], 'concentrations': [200.15053088571014, 39.95440318248273]}}
        unkTableList = [ {
                          "unknown label":k,
                          **{ str("intensity of replicate "+str(1+unkTableMap[k]['intensities'].index(m))):m for m in unkTableMap[k]['intensities'] },
                          **{ str("concentration of replicate "+str(1+unkTableMap[k]['concentrations'].index(n))):n for n in unkTableMap[k]['concentrations'] },
                            "mean of concentrations":unkTableMap[k]['mean'],
                            "sdev of concentrations":unkTableMap[k]['sdev']
                         } for k in unkTableMap.keys()
                         ]
        logger.info("Unknown table list: "+str(unkTableList))
        await context['createAnalysisArtifact']("unk_report.csv", codec.dictArrayToCsv(unkTableList))

        #standard data
        stdDf =  stats[ ( (stats['wellType']=='STANDARD')|(stats['wellType']=='BLANK'))&(stats['analyte']=='ANLT1')].filter(items=["position","analyte","label","knownConcentration","wellReplicateMean","replicateGroup","replicateId"])
        print("\nStd dataframe subset:\n",stdDf)
        workingStdArr = stdDf.to_numpy()
        #print("\nStd array:\n",workingStdArr)

        def aggregateStandards(acc,row):
            value = row[4]
            conc = row[3]
            label = row[2]
            grp = "mean intensity for replicate series " + str(row[5])
            key = (label,conc)
            if (key not in acc):
                acc[key]=collections.OrderedDict()
            acc[key][grp] = value
            return acc

        stdTableMap = reduce(aggregateStandards,workingStdArr,{})
        stdTableList = [ { "type":k[0], "concentration":k[1], **stdTableMap[k] } for k in stdTableMap.keys()  ]
        await context['createAnalysisArtifact']("standard_report.csv", codec.dictArrayToCsv(stdTableList))

        logger.info("Std table map")
        logger.info(str(stdTableMap))
        logger.info("Std table list")
        logger.info(str(stdTableList))

        #successfully generates the 2 plate map reports
        analysisWellsList = [ (well['row']+well['column']).upper() for well in analysisWells ]
        allWellsList = [ (well['row']+well['column']).upper() for well in productWells ]
        print(stats)
        signalResultDict = {}
        calcConcResultDict = {}

        #per analyte, per well data maps
        for analyte in uniqueAnalytes:
            meanSignalDict = {}
            meanCalculatedConcentrationDict = {}
            labelDict = {}
            for well in analysisWellsList:
                rsdf = stats[ (stats['position']==well) & (stats['analyte']==analyte) ]
                signalRes = rsdf['adjustedSignal'].mean()
                meanSignalDict[well]=signalRes

                calcConcRes = rsdf['calculatedConcentration'].mean()
                meanCalculatedConcentrationDict[well] = calcConcRes


            signalResultDict[analyte]=meanSignalDict
            calcConcResultDict[analyte]=meanCalculatedConcentrationDict

        print("\n",signalResultDict)
        print("\n",calcConcResultDict)

        plateRows, plateCols = arraySpotLib.get96WellMap()
        signalDf = pd.DataFrame(columns = plateCols , index=plateRows).fillna('')
        concDf = pd.DataFrame(columns = plateCols , index=plateRows).fillna('')
        labelDf = pd.DataFrame(columns = plateCols , index=plateRows).fillna('')

        signalDict = signalResultDict["ANLT1"]
        concDict = calcConcResultDict["ANLT1"]

        for k,v in signalDict.items():
            r = k[0:1]
            c = int(k[1:])
            signalDf.loc[r,c]=v

        for k,v in concDict.items():
            r = k[0:1]
            c = int(k[1:])
            concDf.loc[r,c]=v

        for k in allWellsList:
            r = k[0:1]
            c = int(k[1:])
            if ( k in analysisWellsDict.keys() ):
                labelDf.loc[r,c]=analysisWellsDict[k]["label"]
            else:
                labelDf.loc[r,c]=""

        print("\nSignal Dataframe:\n",signalDf)
        logger.info("\nLabel Dataframe:\n"+labelDf.to_string())

        plateList = [stdTableList,unkTableList,labelDf,signalDf,concDf]
        headerList = ["standards","unknowns","plate map","replicate mean intensity map","replicate mean calculated concentration map (pg/ml)"]
        await createAnalysisArtifact("intensity_concentration_maps.csv", codec.dataStructuresToCsv(headerList,plateList))

        #no row labels:  a,b,c, etc
        #await createAnalysisArtifact("labels.csv",codec.dictArrayToCsv(labelDf.to_dict(orient="records")))

        plateList = [signalDf,concDf]
        headerList = ["replicate mean intensity map","replicate mean calculated concentration map (pg/ml)"]
        #await analysisArtifactHlpr.storeDataframes("signal_map.csv", "",headerList, plateList)
        await context['createAnalysisArtifact']("intensity_concentration_maps.csv", codec.dataframesToCsv(headerList,plateList))

        #for key in signalResultDict:
        #    await analysisArtifactHlpr.storeCsv("signal_map.csv", "", signalResultDict)
        #await analysisArtifactHlpr.storeCsv("calculatedConcentration_map.csv", "", calcConcResultDict)
        #df['wellReplicateMean'] = df.groupby(['position','analyte'])['adjustedSignal'].transform(np.mean)
        #for well in analysisWellsList:
        #dictionary needed for nice CSV artifact saving
        #test = [ {"row":"A",1:"a1",2:"a2"},{"row":"B",1:"b1",2:"b2"} ]

    await report(stats)

