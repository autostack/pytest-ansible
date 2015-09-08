#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

__author__ = 'Avi Tal <avi3tal@gmail.com>'
__date__ = 'Sep 8, 2015'


class RegisterClasses(type):
    def __init__(cls, name, bases, dct):
        if not hasattr(cls, 'registry'):
            cls.registry = {}
        else:
            cls.registry[name.lower()] = cls
        super(RegisterClasses, cls).__init__(name, bases, dct)
