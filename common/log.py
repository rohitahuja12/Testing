import logging
import datetime
import os
import traceback
from time import gmtime


class MicroSecondsFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        if not datefmt:
            return super().formatTime(record, datefmt=datefmt)

        return datetime.datetime.fromtimestamp(record.created).astimezone().strftime(datefmt)

currentLoggers = {}
def getLogger(name):

    # componentClass = os.environ['COMPONENT_CLASS']
    # phoenixHome = os.environ['PHOENIX_HOME']
    # basepath = os.path.join(phoenixHome, 'logs', componentClass)

    # if not os.path.isdir(os.path.join(phoenixHome, 'logs')):
        # os.mkdir(os.path.joins(phoenixHome, 'logs'))

    # if not os.path.isdir(basepath):
        # os.mkdir(basepath)

    if name not in currentLoggers.keys():
        log = logging.getLogger(name)
        log.setLevel(level=logging.INFO)

        formatter = MicroSecondsFormatter(
            "%(asctime)s [%(name)s] [%(levelname)s] %(message)s",
            "%Y-%m-%d %H:%M:%S.%f %Z")
        formatter.converter = gmtime

        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        ch.setLevel(level=logging.INFO)
        log.addHandler(ch)

        currentLoggers[name] = log

    return currentLoggers[name]


def showTrace(e):
    return ''.join(traceback.format_exception(None, e, e.__traceback__))
