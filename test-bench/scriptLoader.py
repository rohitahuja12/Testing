import os
import os.path
import importlib.util
from dotmap import DotMap

testsDir = './test-bench/tests'

def _getModule(filePath):
    
    name = os.path.basename(filePath)
    spec = importlib.util.spec_from_file_location(name, filePath)
    foo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(foo)
    return foo


def loadScripts():
    # walk over tests directory
    # get list of test scripts
    files = []
    dirlist = [testsDir]
    while len(dirlist) > 0:
        for (dirpath, dirnames, filenames) in os.walk(dirlist.pop()):
            dirlist.extend(dirnames)
            files.extend(map(lambda n: os.path.join(*n), zip([dirpath] * len(filenames), filenames)))
    
    # turn 'em into modules 
    modules = [
        DotMap({"name": os.path.basename(p),
        "module": _getModule(p)})
        for p in files if '.py' == p[-3:]
    ]
    # return them ready to run
    return modules 
