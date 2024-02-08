from statistics import mean
import log
logger = log.getLogger("reader_task_worker.corrections")

def darkImageCorrector(dark):
    def inner(img):
        return img-dark
    return inner

def hotPixelCorrector(hpMask):
    def inner(img):
        imgdata = img.copy()
        shp = imgdata.shape
        for x,row in enumerate(hpMask):
            for y,maskPx in enumerate(row):
                if maskPx:
                    neighbors = [
                        imgdata[a,b]
                        for a in [x-1,x,x+1] 
                        for b in [y-1,y,y+1] 
                        if not(a==x and b==y)
                        and 0 <= a and a < shp[0]
                        and 0 <= b and b < shp[1]
                    ]
                    imgdata[x,y] = mean(neighbors)
        return imgdata
    return inner

def excitationNormCorrector(normImg):
    def inner(img):
        imgdata = img.copy()
        res = img/normImg
        return res
    return inner
