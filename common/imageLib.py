from PIL import Image as PilImage
from PIL.TiffTags import TAGS
import re
import numpy as np
import cv2
import math
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import scipy.ndimage as ndi
import scipy.ndimage.filters as filters
import io
from dotmap import DotMap


def binaryThreshold(image, threshold):

    (_, result) = cv2.threshold(
        image, 
        threshold, 
        255,
        # sys.float_info.max, 
        cv2.THRESH_BINARY)

    return result


def blur(image, radius=5):

    return cv2.blur(image,(radius,radius))


def contourToConvexHull(contour):

    return cv2.convexHull(contour)


def erode(image, radius = 5):

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(radius, radius))
    result = cv2.erode(image, kernel)

    return result


def dilate(image, radius = 5):

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(radius, radius))
    result = cv2.dilate(image, kernel)
    
    return result


def findSpots(image, blurKernelSize, neighborhoodSize, threshold):

    image = blur(image, (blurKernelSize//2)*2+1) # ensure odd

    data_max = filters.maximum_filter(image, neighborhoodSize)
    maxima = (image == data_max)
    data_min = filters.minimum_filter(image, neighborhoodSize)
    diff = ((data_max - data_min) > threshold)
    maxima[diff == 0] = 0

    labeled, num_objects = ndi.label(maxima)
    slices = ndi.find_objects(labeled)
    coords = []

    for dy,dx in slices:
        x_center = (dx.start + dx.stop - 1)/2
        y_center = (dy.start + dy.stop - 1)/2    
        coords.append((int(x_center),int(y_center)))

    spots = [
       {"x":int((dx.start + dx.stop - 1)/2), 
        "y":int((dy.start + dy.stop - 1)/2)}
        for dy,dx
        in slices ]

    spots = list(map(
        lambda s: {
            **s, 
            "brightness": data_max[s["y"],s["x"]],
            "neighborhoodSize": neighborhoodSize,
            "threshold": threshold},
        spots))

    return spots


def getColorCode(colorName: str):
    
    rgb = None

    if colorName == "mat-blue":
        rgb = [41, 182, 246]
    elif colorName == "mat-red":
        rgb = [244, 67, 54]
    elif colorName == "mat-yellow":
        rgb = [255, 235, 59]
    elif colorName == "may-green":
        rgb = [76, 175, 80]
    elif colorName == "blue":
        rgb = [0, 0, 255]
    elif colorName == "red":
        rgb = [255, 0, 0]
    elif colorName == "green":
        rgb = [0, 255, 0]
    else:
        raise Exception("Acceptable color names are: blue")

    def normalizeToBGR(code):
        return list(reversed(code))

    return rgb


def getContours(image):

    gray = image.astype(np.uint8)
    edges = cv2.Canny(gray, 10, 100)

    (contours, _) = cv2.findContours(
            edges, 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE)

    return contours


def getContourCentroid(contour):

    M = cv2.moments(contour)

    if M['m00'] == 0:
        return 0,0

    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])

    return cx,cy


def getContourAspectRatio(contour):

    ellipse = cv2.fitEllipse(contour)
    size = ellipse[1]
    return size[0]/size[1]


def getContourArea(contour):

    return cv2.contourArea(contour)


def getContourBoundSize(contour):

    ellipse = cv2.fitEllipse(contour)
    size = ellipse[1]
    return size[0]*size[1]


def getContourBound(contour):

    x,y,w,h = cv2.boundingRect(contour)
    return { "x": x, "y": y, "width": w, "height": h }


def getContourPeakBrightness(img, contour):
    
    blank = np.zeros((img.shape[0], img.shape[1]), np.uint8)
    mask = cv2.drawContours(blank, contour, -1, color=1, thickness=cv2.FILLED)
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(img, mask)

    return maxVal


# def getClosedContour(contour):

    # newContour = []
    # for i, [(x1,y1)] in enumerate(contour):
        # indx = (i+1) % len(contour)
        # [(x2,y2)] = contour[(i+1) % len(contour)]
        # if abs(x1-x2)>1 or abs(y1-y2)>1:
            # pts = zip(*skimage.draw.line(x1,y1,x2,y2))
            # newContour += [[[x,y]] for x,y in pts][:-1] #last point in line is next point
        # else:
            # newContour += [[[x1,y1]]]

    # newContour = np.array(newContour, np.int32)

    # return newContour


def imageToColorImage(image, scaleFactor=1):

    im = image*scaleFactor
    im = cv2.normalize(im, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
    return cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)


def imageToUint8Image(image):

    image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
    return image.astype(np.uint8)


def invert(image):

    return cv2.bitwise_not(image)


def layerContourLinesColor(image, contours, thickness=1, color=(0,0,255)):

    # clrCode = getColorCode(color)

    # if input image is one-channel
    if len(image.shape) == 2:
        image = imageToColorImage(image)

    imgWithContours = cv2.drawContours(
        image, 
        contours, 
        -1, 
        color, 
        thickness=(thickness==-1 and cv2.FILLED) or thickness)

    return imgWithContours

def loadImage(path):
    return PilImage.open(path)

def loadStack(**kwargs):

    if 'path' in kwargs:
        img = PilImage.open(kwargs['path'])
    elif 'buffer' in kwargs:
        img = PilImage.open(io.BytesIO(kwargs['buffer']))

    def getPositions(img):

        meta_dict = {TAGS[key] : img.tag[key] for key in img.tag.keys()}
        meta_data = meta_dict["ImageJMetaData"]
        meta_data = meta_data[:meta_data.index(b'\xe4')]
        meta_data = bytes.decode(meta_data, 'ASCII').replace('\x00','')

        posLine = re.search(r'POSITIONS:.*\n', meta_data).group()
        positions = re.findall(r'([^\s]*),', posLine)

        return positions

    img.load()
    images = []
    if hasattr(img, "n_frames"):
        positions = getPositions(img)
        for i in range(img.n_frames):
            img.seek(i)
            pxls = np.array(img)

            images.append(pxls)
    else:
        positions = [None]
        f = np.array(img)
        (r,g,b) = cv2.split(f)
        f = cv2.merge([b,g,r])
        images = [f]

    def buildFrame(img, pos, num):
        return DotMap({
            "image":img,
            "position":pos,
            "frame":num
        })
    stack = list(map(buildFrame, images, positions, range(1,len(images)+1)))

    if 'path' in kwargs:
        img.close()

    return stack


def meanThreshold(image, thresholdFactor=1):

    mean = np.mean(image)

    (_, result) = cv2.threshold(
        image, 
        math.floor(mean * thresholdFactor), 
        255,
        # sys.float_info.max, 
        cv2.THRESH_BINARY)

    return result


def medianBlur(image, radius=5):

    return cv2.medianBlur(image,radius)


# If you multithread this function, you're going to have quiet problems
def scatterPlot(xs, ys, xlabel, ylabel):

    fig, ax = plt.subplots(1, figsize=(10,10), dpi=300)
    plot = ax.scatter(xs, ys, s=0.2)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    fig.canvas.draw()
    buff = fig.canvas.buffer_rgba()
    plt.close()

    img = np.asarray(buff)
    (r,g,b,a) = cv2.split(img)
    img = cv2.merge([r,g,b])

    return img


def histogram(vals, bins, xlabel="", ylabel=""):

    fig, ax = plt.subplots(1, figsize=(10,10), dpi=300)
    plot = ax.hist(vals, bins)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    fig.canvas.draw()
    buff = fig.canvas.buffer_rgba()
    plt.close()

    img = np.asarray(buff)
    (r,g,b,a) = cv2.split(img)
    img = cv2.merge([r,g,b])

    return img


def constrainBrightness(img, lower, upper):

    res = np.where(img>upper,upper,img)
    res = np.where(res<lower,lower,res)

    return res

def convolve2D(image, kernel, padding=0, strides=1):
    # Cross Correlation
    kernel = np.flipud(np.fliplr(kernel))

    # Gather Shapes of Kernel + Image + Padding
    xKernShape = kernel.shape[0]
    yKernShape = kernel.shape[1]
    xImgShape = image.shape[0]
    yImgShape = image.shape[1]

    # Shape of Output Convolution
    xOutput = int(((xImgShape - xKernShape + 2 * padding) / strides) + 1)
    yOutput = int(((yImgShape - yKernShape + 2 * padding) / strides) + 1)
    output = np.zeros((xOutput, yOutput))

    # Apply Equal Padding to All Sides
    if padding != 0:
        imagePadded = np.zeros((image.shape[0] + padding*2, image.shape[1] + padding*2))
        imagePadded[int(padding):int(-1 * padding), int(padding):int(-1 * padding)] = image
        print(imagePadded)
    else:
        imagePadded = image

    # Iterate through image
    for y in range(image.shape[1]):
        # Exit Convolution
        if y > image.shape[1] - yKernShape:
            break
        # Only Convolve if y has gone down by the specified Strides
        if y % strides == 0:
            for x in range(image.shape[0]):
                # Go to next row once kernel is out of bounds
                if x > image.shape[0] - xKernShape:
                    break
                try:
                    # Only Convolve if x has moved by the specified Strides
                    if x % strides == 0:
                        output[x, y] = (kernel * imagePadded[x: x + xKernShape, y: y + yKernShape]).sum()
                except:
                    break

    return output

def findCircleNearestPoint(image, minRadius:int, thresholdFactor:int, targetPoint):

    ptX = targetPoint[0]
    ptY = targetPoint[1]

    thresh = meanThreshold(image,thresholdFactor )

    contours = getContours(thresh)

    def filterBySize(circle,size):
        (x,y),radius = circle
        return radius>size

    def rankByPoint(circle):
        (x,y),radius = circle
        return math.hypot(x-ptX,y-ptY)

    circles = map(cv2.minEnclosingCircle,contours)
    filteredCircles = filter(lambda x:filterBySize(x,minRadius),circles)
    sortedCircles = sorted(filteredCircles, key=rankByPoint)

    center = next(((int(x),int(y)) for (x,y),radius in sortedCircles), targetPoint)
    return center

def subimage(image, startRow: int, endRow: int, startCol: int, endCol: int):
    sub = image[startRow:endRow,startCol:endCol]
    return sub

def findNearestPoint(all_points, target_point):
    closest = None
    min_distance = float('inf')
    for point in all_points:
        distance = math.sqrt((point[0] - target_point[0])**2 + (point[1] - target_point[1])**2)
        if distance < min_distance:
            min_distance = distance
            closest = point

    return closest