#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os
import threading
import time

from pytest_ansible.settings import REDIS_CHANNEL
from pytest_ansible.redisq import RedisQueue


class Dispatcher(threading.Thread):
    # FIXME: quick and dirty
    def __init__(self):
        super(Dispatcher, self).__init__()
        self.active = True
        self.socket = RedisQueue(REDIS_CHANNEL)
        # cache nodes
        self._nodes = dict()

    def register(self, nodes):
        # FIXME: currently only register to dictionary
        self._nodes.update({node.name: node for node in nodes})

    def run(self):
        while self.active:
            try:
                data = self.socket.get()
                if data is not None:
                    if data.get('halt', False):
                        self.active = False
                        continue
                    func = '_load_{module_name}'.format(**data['data']['invocation'])
                    getattr(self._nodes[data['host']], func)(data['data'])
                    # FIXME: replace with log
                    print('dispatcher thread id is', self, threading.currentThread(), os.getpid())
            except (AttributeError, KeyError, TypeError) as err:
                # FIXME: replace with log
                print(err)

            time.sleep(0.1)

    def close(self):
        self.socket.put({'halt': True})
        self.join()

