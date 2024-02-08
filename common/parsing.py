import json
import types


def jsonToObj(string):

    return json.loads(
        string, 
        object_hook = lambda d: types.SimpleNamespace(**d))
    
