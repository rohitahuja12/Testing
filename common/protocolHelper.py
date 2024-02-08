import sys
import os
import importlib
import log
logger = log.getLogger('common.protocolHelper')

_protocols = None
def _getProtocols(protocolDir, protocolImportPrefix):

    import sys
    logger.info(f'adding {protocolDir} to path')
    sys.path.insert(0, protocolDir)

    global _protocols
    if not _protocols:

        protocolNames = [n.replace('.py','') 
            for n in os.listdir(protocolDir) 
            if n[:2] != '__']

        def loadProtocol(name):
            return importlib.import_module(protocolImportPrefix + name)

        ps = [{
            'name': n, 
            'module':loadProtocol(n), 
        } for n in protocolNames]

        def maybeGetSchema(p):
            try:
                return p['module'].argSchema
            except:
                return None

        _protocols = [{
            **p,
            'argSchema':maybeGetSchema(p)
        } for p in ps]

    return _protocols

protocolCache = {}
def getProtocols(protocolDir, protocolImportPrefix):
    key = (protocolDir, protocolImportPrefix)
    if not (key in protocolCache):
        protocolCache[key] = _getProtocols(protocolDir, protocolImportPrefix)
    return protocolCache[key]

def getProtocolsDict(protocolDir, protocolImportPrefix):
    ps = getProtocols(protocolDir, protocolImportPrefix)
    return { x['name']: x for x in ps }
