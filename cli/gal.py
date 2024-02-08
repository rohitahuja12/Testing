import json
from pyparsing import *
import numpy as np
import functools

q = Optional(Literal('"')).suppress()
eq = Literal("=").suppress()
nl = LineEnd().suppress()
tab = White().suppress()
rest = restOfLine.suppress() + nl

def ATFLine():
    line = Group(Literal("ATF") + Word(nums) + rest)
    return line.setResultsName("ATFLine")

def structuralInfoLine():
    line = Group(Word(nums) + Word(nums) + rest)
    return line.setResultsName("structuralInfoLine")

def keyValueLine():
    line = Group(q + Word(alphanums) + eq + Word(alphanums+".:/ ").leaveWhitespace() + q + rest)
    return line.setResultsName("keyValueLine")

def paramLine():
    key = Word(printables)
    value = OneOrMore(Word(printables))
    line = Group(key + tab + value + rest)
    return line.setResultsName("paramLine")

def typeLine():
    line = Group( q + Literal("Type") + eq + restOfLine)
    return line.setResultsName("typeLine")


def blockTypeLine():
    line = Group( q + Literal("BlockType") + eq + Word(nums) + rest )
    return line.setResultsName("blockTypeLine")

def blockCountLine():
    line = Group( q + Literal("BlockCount") + eq + Word(nums) + rest )
    return line.setResultsName("blockCountLine")

def URLLine():
    line = Group( q + Literal("URL") + eq + Word(printables) + restOfLine )
    return line.setResultsName("URLLine")

def blockLine():
    block = Literal("Block").suppress()
    line = Group( q + block + Word(alphanums) + eq + delimitedList(Word(nums),",") + q + rest)
    return line

def spotHeaderLine():
    Block, Row, Column, ID = map(Literal, ["Block","Row","Column","ID"])
    line = \
        Literal("Block") + \
        Literal("Row") + \
        Literal("Column") + \
        (Literal("ID") | Literal("Name")) + \
        rest
    return line.setResultsName("spotHeaderLine")

def spotLine():
    well = Word(alphanums)
    row = Word(nums)
    col = Word(nums)
    name = Word(alphanums+"-")
    line = Group(well + tab + row + tab + col + tab + name + rest)
    return line.setResultsName("spotLine")


async def handle(args):

    galPath = args["<galFilePath>"]
    outPath = args["<outputFilePath>"]

    docParser = \
        ATFLine() + \
        structuralInfoLine() + \
        typeLine() + \
        OneOrMore(blockTypeLine() | blockCountLine() | URLLine()) + \
        OneOrMore(blockLine()).setResultsName("blockLines") + \
        spotHeaderLine() + \
        OneOrMore(spotLine()).setResultsName("spotLines")
    parseResult = docParser.parseFile(galPath)

    # print(parseResult.dump())

    galDict = {
        "blocks": {
            l[0]: {
                "topLeftX": l[1],
                "topLeftY": l[2],
                "featureDiameter": l[3],
                "xFeatures": l[4],
                "xSpacing": l[5],
                "yFeatures": l[6],
                "ySpacing": l[7]
            }
            for l in parseResult.blockLines
        },
        "blockDescription": {
            "spots": [
                {
                    "row": l[1],
                    "col": l[2],
                    "name": l[3]
                }
                for l in parseResult.spotLines
                # only iterate over the first block
                # assume all blocks are same for now
                if l[0] == parseResult.spotLines[0][0]
            ]
        }
    }
    
    res = json.dumps(galDict, indent=4)
    if outPath:
        with open(outPath, "w") as outfile:
            outfile.write(res)
    else:
        print(res)
