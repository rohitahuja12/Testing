from time import time
import itertools
from functools import reduce

def indices(xs, baseValue=1):
    return range(baseValue, len(xs)+baseValue)


class dotdict(dict):

    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def flatmap(f, *items):
    return itertools.chain.from_iterable(map(f, *items))


def flatten(items):
    return list(itertools.chain.from_iterable(items))


def constant(x):
    return itertools.cycle([x])


def timeIt(func):
    # This function shows the execution time of 
    # the function object passed
    def wrap_func(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        print(f'Function {func.__name__!r} executed in {(t2-t1):.4f}s')
        return result
    return wrap_func


def chain(fs):
    return reduce(lambda f, g: lambda x: g(f(x)), fs)


def strip(dct, name):
    return {k:dct[k] for k in dct if k != name}


def cfilter(f):
    def inner(xs):
        return list(filter(f, xs))
    return inner


def cmap(f):
    def inner(xs):
        return list(map(f, xs))
    return inner


def csort(f):
    def inner(xs):
        return list(sorted(xs, key=f))
    return inner

def bisect(pred, xs):
    left = itertools.takewhile(pred, xs)
    right = itertools.dropwhile(pred, xs)
    return left, right
