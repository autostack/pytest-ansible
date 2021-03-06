#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import socket


class RegisterClasses(type):
    def __init__(cls, name, bases, dct):
        if not hasattr(cls, 'registry'):
            cls.registry = {}
        else:
            cls.registry[name.lower()] = cls
        super(RegisterClasses, cls).__init__(name, bases, dct)


def get_open_port(host='127.0.0.1'):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


# def memoize(f):
#     """
#     Memoization decorator for a function taking a single argument
#     """
#     class memodict(dict):
#         def __missing__(self, key):
#             ret = self[key] = f(key)
#             return ret
#     return memodict

def memoize(f):
    """
    Memoization decorator for a function taking one or more arguments
    """
    class memodict(dict):
        def __getitem__(self, *key):
            return dict.__getitem__(self, key)

        def __missing__(self, key):
            ret = self[key] = f(*key)
            return ret

    return memodict().__getitem__
