import json
import os
import csv
import io
import numpy as np
from PIL import Image as PilImage
import log
import dataclasses
import textwrap

logger = log.getLogger("common.artifactCodec")

class ArtifactCodec:


    def __init__(self):
        self.stringEncoding = 'utf-8'


    def dictToJson(self, data):
        """ 
        Takes a dictionary of data, jsonifies it, stores it 
        """
        jsonObj = bytes(json.dumps(data, indent=4), self.stringEncoding)

        return jsonObj


    def jsonToDict(self, data):
        """
        Deserializing partner to dictToJson
        """
        jsonObj = json.loads(data)

        return jsonObj

    def dataclassObjectArrayToCsv(self, dataList):
        output = io.StringIO()
        headerWritten = False
        for dataObject in dataList:
            data = dataclasses.asdict(dataObject)
            if not headerWritten:
                fieldNames = list(data.keys())
                writer = csv.DictWriter(output,fieldnames=fieldNames)
                writer.writeheader()
                headerWritten = True
            writer.writerow(data)

        dataResult = bytes(output.getvalue(), self.stringEncoding)
        return dataResult

    def dictToCsv(self, data):
        output = io.StringIO()

        fieldNames = list(data.keys())

        print(fieldNames)

        writer = csv.DictWriter(output,fieldnames=fieldNames)
        writer.writeheader()
        writer.writerow(data)
        dataResult = bytes(output.getvalue(), self.stringEncoding)
        return dataResult

    def arrayToCsv(self, twoDeeArray):
        output = io.StringIO()
        writer = csv.writer(output)

        for row in twoDeeArray:
            writer.writerow(row)

        data = bytes(output.getvalue(), self.stringEncoding)
        return data

    def listToText(self, aList):
        output = io.StringIO()
        for row in aList:
            wrappedText = textwrap.fill(row, width = 120)
            output.write(wrappedText+"\n")
        data = bytes(output.getvalue(),self.stringEncoding)
        return data

    def dataStructuresToCsv(self, headerList, data):
        output = io.StringIO()
        writer = csv.writer(output)
        i=0;
        for df in data:
            if len(df) > 0:
                output.write(headerList[i])
                output.write("\n")
                if ( isinstance(df,list) ):
                    if len(df) > 0:
                        header = df[0].keys()
                        writer.writerow(header)
                    for item in df:
                        writer.writerow(item.values())
                else:
                    df.to_csv(output)

                writer.writerow("\n")
                i=i+1
        data = bytes(output.getvalue(), self.stringEncoding)
        return data 


    def dictArrayToCsv(self, data):
        """ 
        Takes a list of repeated dictionaries, stores it as csv
        """
        output = io.StringIO()
        writer = csv.writer(output)



        # def groupByKeys(acc, item):
            # if item.viewkeys() == acc['currentKeys']:
                # acc['groups'][-1].append(item)
            # else:
                # acc['groups'].append([item])
        # groupedData = reduce(
            # groupByKeys, 
            # data, 
            # {'currentKeys':{}, 'groups':[]}
        # )['groups']

        # for group in groupedData:
        if len(data) > 0:
            header = data[0].keys()
            writer.writerow(header)
            for item in data:
                writer.writerow(item.values())
                # writer.writerow("")

        data = bytes(output.getvalue(), self.stringEncoding)
        return data

    def csvToDictArray(self, data):
        """
        Deserializing partner to dictsToCsv
        """
        data = data.decode(self.stringEncoding)
        lines = data.split('\n')

        reader = csv.DictReader(lines)
        output = [i for i in reader]

        return output


    def arrayToTiff(self, data, prefix=None):

        buffer = io.BytesIO()
        im = PilImage.fromarray(data)
        im.save(buffer, format='tiff')

        return prefix + buffer.getvalue() if prefix else buffer.getvalue()


    def tiffToArray(self, data, prefixBytes=0):

        prefix = data[:prefixBytes]
        data = data[prefixBytes:]
        buffer = io.BytesIO(data)
        img = PilImage.open(buffer)
        arrayImage = np.array(img)

        return (prefix, arrayImage) if prefixBytes else arrayImage

    def readTiff(self, path):
        img = PilImage.open(path)
        return img

    def arrayToTiffStack(self, data):
        """ Stores an image, assumes stack """
        outputBuffer = io.BytesIO()

        imlist = [PilImage.fromarray(i) for i in data]
        imlist[0].save(outputBuffer, format='tiff', save_all=True, append_images=imlist[1:])

        return outputBuffer.getvalue()


    def saveTiff(self, filePath, data):
        img = PilImage.fromarray(data)
        img.save(filePath, format='tiff')

    def tiffStackToArray(self, data):
        """ Retrieve an image stack """
        buffer = io.BytesIO(data)

        # this is shamelessly copied from mpascucci/multipagetiff
        im = PilImage.open(buffer)
        i = 0
        frames = []
        try:
            while True:
                im.seek(i)
                frames.append(np.array(im))
                i += 1
        except EOFError:
            pass

        return frames

    def figToPng(self, data):
        buffer = io.BytesIO()
        data.savefig(buffer)
        buffer.seek(0)
        im = PilImage.open(buffer)
        im.save(buffer, format='png')
        #res = await self.artifactStorageManager.storeArtifact(name, buffer.getvalue())
        return buffer.getvalue()



    def arrayToJpg(self, data, quality=100, subsampling=0, prefix=None):
        """ Stores a jpg img """
        buffer = io.BytesIO()

        im = PilImage.fromarray(data)
        if im.mode != 'RGB':
            im = im.convert('RGB')
        # quality and subsampling are required to get identical image saves, jpg sux
        im.save(buffer, 
            format='JPEG', 
            quality=quality, 
            subsampling=subsampling)

        return prefix + buffer.getvalue() if prefix else buffer.getvalue()


    def jpgToArray(self, data, prefixBytes=0):
        """ Retrieve a jpg img """
        prefix = data[:prefixBytes]
        data = data[prefixBytes:]
        buffer = io.BytesIO(data)
        img = PilImage.open(buffer)
        arrayImage = np.array(img)

        return (prefix, arrayImage) if prefixBytes else arrayImage


    def compressJpg(self, data, quality):
        """ Return a compressed jpg img, quality 1-100 """
        bufferIn = io.BytesIO(data)
        bufferOut = io.BytesIO()

        img = PilImage.open(bufferIn)
        img.save(bufferOut, format='JPEG', quality=quality)

        return bufferOut.getvalue()
