import numpy as np
import math
import scipy.optimize as opt
import log

from numpy.polynomial.chebyshev import Chebyshev as cheby
# import pyplot as plt

logger=log.getLogger('analyzer.src.main')

def logistic5(x,a,b,c,d,g):
   return ((a-d)/((1.0+((x/c)**b))**g) ) + d

def logistic5Inverse(y, a, b, c, d, g):
    return c * ( ( ( ((a-d)/(y-d))**(1/g)) - 1 )**(1.0/b) )

#source: https://ipython-books.github.io/93-fitting-a-function-to-data-with-nonlinear-least-squares/
#https://www.myassays.com/four-parameter-logistic-regression.html
def logistic4(x, a, b, c, d):
    #(a) is the minimum asymptote, (b) is the steepness, (c) is the inflection point and (d) is the maximum asymptote.# for this equation best guesses might be:
    #a = np.min(y)
    #d = np.max(y)
    #c = (a+d) / 2
    #b = 1
    return ((a-d)/(1.0+((x/c)**b))) + d

def logistic4Inverse(y, a, b, c, d):
    return c * ( ( ((a-d)/(y-d)) - 1 )**(1.0/b) )

def calculateWeights(rx,ry):
    x = []
    y = []
    #remove negative intensity values
    for xi,yi in zip(rx,ry):
        if yi>0:
            x.append(xi)
            y.append(yi)
        else:
            logger.info(f"Removed negative values {xi},{yi}")
    groupedY = {xi: [y[j] for j, xj in enumerate(x) if xj == xi] for xi in set(x)}
    sdevByX = {}
    for xi,yi in groupedY.items():
        if len(yi) > 1:
            sdevByX.update({xi:np.std(yi,ddof=1)})
        else:
            value = yi[0]
            sdevByX.update({xi:value})
    weights = [ sdevByX[xi] for xi in x ]
    return x,y,weights

def fit4(rx,ry):
    x,y,weights = calculateWeights(rx,ry)
    a = np.min(y)
    d = np.max(y)
    c = (np.min(x) + np.max(x)  ) / 2
    b = 1
    initialGuesses = [a,b,c,d]
    (a_, b_, c_, d_), _ = opt.curve_fit(logistic4, x, y,p0=initialGuesses,  sigma=weights, absolute_sigma=True, maxfev = 100000)
    residuals = y - logistic4(x, a_,b_,c_,d_)
    ss_res = np.sum(residuals**2)
    return (a_, b_, c_, d_), ss_res

def fit5(rx,ry):
    x,y,weights = calculateWeights(rx,ry)
    a = np.min(y)
    d = np.max(y)
    c = (np.min(x)+ np.max(x)  ) / 2
    b = 1
    g = 1
    initialGuesses = [a,b,c,d,g]
    (a_, b_, c_, d_, g_), _ = opt.curve_fit(logistic5, x, y,p0=initialGuesses,  sigma=weights, absolute_sigma=True, maxfev = 100000)

    residuals = y - logistic5(x, a_,b_,c_,d_,g_)
    ss_res = np.sum(residuals**2)

    return (a_, b_, c_, d_, g_), ss_res

def getPlot(x,y):
    (a,b,c,d) = fit4(x,y)
    xfit = np.logspace(start=-4, stop=4, num = 100,base=10.0,endpoint=True)
    yfit = logistic4(xfit, a, b, c, d)
    return xfit,yfit


def getValidRanges(lowConc, hiConc, pdFunc, targetFunc, avgFunc, curveFlag):
    avgLow = avgFunc(lowConc)
    avgHi = avgFunc(hiConc)
    targetHi = targetFunc(hiConc)
    targetLow = targetFunc(lowConc)

    hiIntensity = max(avgHi,targetHi)
    hiPD = pdFunc(hiIntensity)

    #if the chosen upper value is out of range, select the lesser of the two
    if (math.isnan(hiPD)):
        logger.info("Hi PD was nan, choosing lower upper value")
        hiIntensity = min(avgHi, targetHi)

    #set the start range if seeking the solution for the lower curve
    if curveFlag == "lower":
        lowIntensity = avgFunc(lowConc)
    else:
        lowIntensity = targetFunc(lowConc)

    lowIntensityRange = avgFunc(lowConc)

    logger.info(f"Curve flag: {curveFlag}")
    logger.info(f"Low and Hi conc: {lowConc} and {hiConc}")
    logger.info(f"Low and Hi avg intensities: {avgLow} and {avgHi}")
    logger.info(f"Low and Hi target intensities: {targetLow} and {targetHi}")
    logger.info(f"Low and Hi PDs at avg: {pdFunc(avgLow)} and {pdFunc(avgHi)}")
    logger.info(f"Low and Hi PDs at target: {pdFunc(targetLow)} and {pdFunc(targetHi)}")
    logger.info(f"Low and Hi intensities after selection: {lowIntensity} and {hiIntensity}")
    logger.info(f"Finding roots in range: {lowIntensity} to {hiIntensity}")

    c_lambda = cheby.interpolate(pdFunc,512,domain=[lowIntensity,hiIntensity])
    g_lambda = c_lambda - 20
    roots_lambda = g_lambda.roots()
    filtered_roots_lambda = roots_lambda[(roots_lambda >= lowIntensityRange) & (roots_lambda <= hiIntensity)]
    res = filtered_roots_lambda[np.isreal(filtered_roots_lambda)].real.tolist()
    logger.info(f"Found roots: {res}")
    if pdFunc(avgLow) < 20:
        res.insert(0,avgFunc(lowConc))
    if len(res) % 2 != 0:
        res.append(hiIntensity)
    resList = []
    for n in range (0,len(res),2):
        item = []
        item.append(res[n])
        item.append(res[n+1])
        resList.append(item)
    logger.info(f"Adjusted roots: {resList}")
    logger.info("")
    return resList

def findOverlaps(a, b):
    #if one or the other has no values, then return empty
    if len(a) == 0 or len(b) == 0:
        return []
    res = []
    for ai in a:
        for bi in b:
            newInterval = []
            if ai[0] >= bi[0] and ai[1] <= bi[1]:     #a is completely in b :  --===--
                res.append(ai)
            elif ai[0] <= bi[0] and ai[1] >= bi[0] and ai[1] <= bi[0]:   #  ___==-- right side of a is in b
                newInterval.append(bi[0])
                newInterval.append(ai[1])
            elif ai[0] >= bi[0] and ai[0] <= bi[1] and ai[1] >= bi[1]:  #  --==__ left side of a is in b
                newInterval.append(ai[0])
                newInterval.append(bi[1])
            elif bi[0] >= ai[0] and bi[1] <= ai[1]:     #b is completely in a :  --===--
                res.append(bi)
            elif bi[0] <= ai[0] and bi[1] >= ai[0] and bi[1] <= ai[0]:   #  ___==-- right side of b is in a
                newInterval.append(ai[0])
                newInterval.append(bi[1])
            elif bi[0] >= ai[0] and bi[0] <= ai[1] and bi[1] >= ai[1]:  #  --==__ left side of b is in a
                newInterval.append(bi[0])
                newInterval.append(ai[1])
            if len(newInterval) > 0:
                res.append(newInterval)
    return res