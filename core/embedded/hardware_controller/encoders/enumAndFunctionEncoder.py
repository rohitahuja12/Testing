import inspect
import json
import types
from enum import Enum

# allow functions and enums to be serialized
class EnumAndFunctionEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return str(obj)
        if isinstance(obj, (types.LambdaType, types.FunctionType, types.MethodType)):
            return "Function: " + obj.__name__ + str(inspect.signature(obj))
        return json.JSONEncoder.default(self, obj)

