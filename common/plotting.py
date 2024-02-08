import coords
import matplotlib.pyplot as plt
import matplotlib.transforms as transformTo
import matplotlib.scale as scale
from matplotlib.ticker import FuncFormatter
import numpy as np
import io
import typing
from math import log
from dataclasses import dataclass
import log as lg
logger = lg.getLogger('common.plotting')

@dataclass
class Instruction():
    pass

@dataclass
class Title(Instruction):
    title: str = ""
    fontsize: int = 18

@dataclass
class Background(Instruction):
    color: str = "white"

@dataclass
class Point(Instruction):
    pt: coords.Point
    name: str = ""
    color: str = "blue"
    marker: str = "o"
    markersize: int = 2
@dataclass
class Curve(Instruction):
    pts: typing.List[coords.Point]
    color: str = "blue"
    linestyle: str = "solid"

@dataclass
class Function(Instruction):
    function: typing.Callable[[float], float]
    color: str = "blue"
    alpha: float = 1.0
    linestyle: str = "solid"
    dependentaxis: str = "y"

@dataclass
class Box(Instruction):
    tl: coords.CoordTriplet
    br: coords.CoordTriplet
    name: str = ""
    color: str = "blue"
    linestyle: str = "solid"

@dataclass
class Text(Instruction):
    label: str = ""
    x: int = 0
    y: int = 0
    fontsize: int = 18
    horizontalalignment: str = "left"
    verticalalignment: str = "bottom"

@dataclass
class ShadedXRegion(Instruction):
        minX: int
        maxX: int
        color: str='lightgreen'
        alpha: float=0.2

@dataclass
class XIncreasesLTR(Instruction):
    pass

@dataclass
class XIncreasesRTL(Instruction):
    pass

@dataclass
class YIncreasesBTT(Instruction):
    pass

@dataclass
class YIncreasesTTB(Instruction):
    pass

@dataclass
class XYScalesEqual(Instruction):
    pass

@dataclass
class XScaleLinear(Instruction):
    pass

@dataclass
class YScaleLinear(Instruction):
    pass

@dataclass
class XScaleLog(Instruction):
    base: int = 2

@dataclass
class YScaleLog(Instruction):
    base: int = 2

@dataclass
class XMin(Instruction):
    xmin: int

@dataclass
class XMax(Instruction):
    xmax: int

@dataclass
class YMin(Instruction):
    ymin: int

@dataclass
class YMax(Instruction):
    ymax: int

@dataclass
class Height(Instruction):
    height: int

@dataclass
class Width(Instruction):
    width: int

@dataclass
class XLabel(Instruction):
    label: str
    fontsize: int

@dataclass
class YLabel(Instruction):
    label: str
    fontsize: int

def addShadedXRegion(shadedXRegion):
    #if shadedXRegion.minX is not None and shadedXRegion.maxX is not None:
    logger.info(f"Adding shaded region for: {shadedXRegion.minX} to {shadedXRegion.maxX}")
    plt.axvspan(shadedXRegion.minX,shadedXRegion.maxX,facecolor=shadedXRegion.color,alpha=shadedXRegion.alpha)

def addPt(pt):
    plt.plot(pt.pt.x, pt.pt.y, marker=pt.marker, markersize=pt.markersize, color=pt.color)
    plt.text(
        pt.pt.x * (1 + 0.0001), 
        pt.pt.y * (1 + 0.0001), 
        pt.name, 
        fontsize=8)
    
def addBox(box):
    plt.plot(
        [box.tl.x, box.br.x, box.br.x, box.tl.x, box.tl.x],
        [box.tl.y, box.tl.y, box.br.y, box.br.y, box.tl.y],
        color=box.color,
        linestyle=box.linestyle
    )
    plt.text(
        box.tl.x * (1 + 0.0001), 
        box.tl.y * (1 + 0.0001), 
        box.name, 
        fontsize=8)

def addCurve(curve):
    plt.plot(
        [p.x for p in curve.pts],
        [p.y for p in curve.pts],
        color=curve.color,
        linestyle=curve.linestyle
    )

def addFunction(function):
    if (function.dependentaxis == 'y'):
        lower,upper = plt.xlim()
        domain = np.logspace(
            start=log(lower,10),
            stop=log(upper,10),
            base=10,
            endpoint=True,
            num=100)
        range = [function.function(d) for d in domain]
    elif (function.dependentaxis == 'x') :
        lower,upper = plt.ylim()
        range = np.logspace(
            start=log(lower,10),
            stop=log(upper,10),
            base=10,
            endpoint=True,
            num=100)
        domain = [function.function(r) for r in range]
    else:
        raise Exception (f'Unsupported dependent axes.  Allowable values are x and y.  Provided: {function.dependentaxis}')

    #scale is always log atm!
    # when we want to use this for linear-scale
    # plots, we need to change how this logspace
    # generator works, probably passing some state
    # around about the plot. Getting the scale 
    # log/lin/etc is not easy to find.
    # 10**n=left, 10**m=right

    plt.plot(
        domain,
        range,
        color=function.color,
        alpha=function.alpha,
        linestyle=function.linestyle
    )

def addText(text):
    plt.text(text.x, text.y, text.label, fontsize=text.fontsize, horizontalalignment=text.horizontalalignment, verticalalignment=text.verticalalignment)

def plot(instructions):
    #clear previous plot info
    plt.clf()

    height = next(
        (i.height for i in instructions if isinstance(i, Height)),
        500
    )
    width = next(
        (i.width for i in instructions if isinstance(i, Width)), 
        500
    )
    px = 1/plt.rcParams['figure.dpi']  # pixel in inches
    # plt.figure(figsize=(width*px, height*px))
    fig, ax = plt.subplots(figsize=(width*px, height*px))

    for i in instructions:
        if isinstance(i, Background):
            ax.set_facecolor(color=i.color)

    for i in instructions:
        if isinstance(i, XIncreasesLTR):
            pass
        if isinstance(i, XIncreasesRTL):
            plt.gca().invert_xaxis()
        if isinstance(i, YIncreasesBTT):
            pass
        if isinstance(i, YIncreasesTTB):
            plt.gca().invert_yaxis()
        if isinstance(i, XLabel):
            plt.xlabel(i.label, fontsize=i.fontsize)
        if isinstance(i, YLabel):
            plt.ylabel(i.label, fontsize=i.fontsize)
        if isinstance(i, Title):
            ax.set_title(i.title, fontsize=i.fontsize)
        if isinstance(i, XYScalesEqual):
            plt.gca().set_aspect('equal', adjustable='box')
        if isinstance(i, XScaleLinear):
            plt.xscale("linear")
        if isinstance(i, YScaleLinear):
            plt.yscale("linear")
        if isinstance(i, XScaleLog):
            plt.xscale("log", base=i.base)
        if isinstance(i, YScaleLog):
            plt.yscale("log", base=i.base)
        if isinstance(i, XMin):
            plt.xlim(xmin=i.xmin)
        if isinstance(i, XMax):
            plt.xlim(xmax=i.xmax)
        if isinstance(i, YMin):
            plt.ylim(ymin=i.ymin)
        if isinstance(i, YMax):
            plt.ylim(ymax=i.ymax)

    for i in instructions:
        if isinstance(i, Point):
            addPt(i)
        if isinstance(i, Box):
            addBox(i)
        if isinstance(i, Curve):
            addCurve(i)
        if isinstance(i, Function):
            addFunction(i)
        if isinstance(i, Text):
            addText(i)
        if isinstance(i, ShadedXRegion):
            addShadedXRegion(i)

    frmt = FuncFormatter(lambda y, _: '{:.16g}'.format(y))
    ax.get_xaxis().set_major_formatter(frmt)
    ax.get_yaxis().set_major_formatter(frmt)

    buff = io.BytesIO()
    plt.savefig(buff, format="jpg")

    return buff.getbuffer()
    

