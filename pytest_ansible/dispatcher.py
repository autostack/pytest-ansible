#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import threading
import time


__author__ = 'Avi Tal <avi3tal@gmail.com>'
__date__ = 'Sep 9, 2015'


class Dispatcher(threading.Thread):
    def __init__(self, queue, env):
        super(Dispatcher, self).__init__()
        self._q = queue
        self.inventory = env
        self.active = True

    def _dispatch(self, host, data):
        nodes = self.inventory.all.filter(address=host)[0]
        try:
            getattr(nodes, '_load_' + data['invocation']['module_name'])(data)
        except AttributeError:
            pass

    def run(self):
        while self.active:
            msg = self._q.get()
            if isinstance(msg, str) and msg == 'quit':
                break
            if msg is None:
                time.sleep(2)
                continue

            # TODO: handle eval exception
            msg = eval(msg)
            if isinstance(msg, tuple):
                self._dispatch(*msg)

    def close(self):
        self.active = False
