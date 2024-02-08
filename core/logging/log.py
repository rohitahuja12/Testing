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
