#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from rq import Connection, Queue, Worker

__author__ = 'Avi Tal <avi3tal@gmail.com>'
__date__ = 'Sep 6, 2015'


if __name__ == '__main__':
    # Tell rq what Redis connection to use
    with Connection():
        q = Queue()
        Worker(q).work()
