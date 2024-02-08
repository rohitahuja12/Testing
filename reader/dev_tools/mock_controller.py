import sys
sys.path.insert(0, '.')
import reader.lib_hardware_interface.client as hwclient
# from typing import List

def some_func(x:int) -> int:
    return x

def f2(many: list) -> list:
    return many

def add(a:int, b:int) -> int:
    return a+b

hwclient.HardwareRequestServer(
    transport="tcp://127.0.0.1:1234",
    commandTable={ 
        "do": some_func,
        "do_many": f2,
        "add": add
    })

