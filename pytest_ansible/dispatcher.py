#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os
import threading
import zmq
import time
from pytest_ansible.settings import ZMQ_PORT
from pytest_ansible.zmqsocket import Socket


class Dispatcher(threading.Thread):
    # FIXME: quick and dirty
    def __init__(self):
        super(Dispatcher, self).__init__()
        self.active = True
        self.context = zmq.Context()
        self.socket = Socket(self.context, zmq.PULL)
        self.socket.connect("tcp://localhost:%s" % ZMQ_PORT)

        # cache nodes
        self._nodes = dict()

    def register(self, nodes):
        # FIXME: currently only register to dictionary
        self._nodes.update({node.name: node for node in nodes})

    def run(self):
        while self.active:
            try:
                # data = self.socket.recv_json(flags=zmq.NOBLOCK)
                data = self.socket.recv_json(timeout=3)
                if data is not None:
                    func = '_load_{module_name}'.format(**data['data']['invocation'])
                    getattr(self._nodes[data['host']], func)(data['data'])
                    # FIXME: replace with log
                    print('dispatcher thread id is', self, threading.currentThread(), os.getpid())
            except (AttributeError, KeyError, TypeError) as err:
                # FIXME: replace with log
                print(err)

            time.sleep(0.1)

    def close(self):
        self.active = False
        self.join()

        # close zmq must be done after join thread
        self.socket.close()
        self.context.term()

