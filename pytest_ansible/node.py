#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from pytest_ansible.utils import memoize
import threading
import os


class Facts(dict):
    PREF = 'ansible_'

    def __getattr__(self, attr):
        try:
            data = self[attr]
        except KeyError:
            if attr.startswith(self.PREF):
                raise
            attr = '{}{}'.format(self.PREF, attr)
            data = getattr(self, attr)
        if isinstance(data, dict):
            data = Facts(data)
        return data


class Node(object):
    def __init__(self, name, inventory):
        self._name = name
        self._inventory = inventory
        self._facts = None

    def __repr__(self):
        repr_template = ("<{0.__class__.__module__}.{0.__class__.__name__}"
                         " object at {1} | name {2}>")
        return repr_template.format(self, hex(id(self)), self.name)

    def _load_setup(self, data):
        print('node thread id is', threading.currentThread(), os.getpid())
        self._facts = Facts(data['ansible_facts'])

    @property
    def facts(self):
        return self._facts

    @property
    def vars(self):
        return self.inventory.get_host(self._name).vars

    @property
    def name(self):
        return self._name

    @property
    def inventory(self):
        return self._inventory


@memoize
def get_node(name, inventory):
    '''
    Generating Node object base on given ansible host instance
    :param name: host name
    :param inventory: inventory manager instance
    :return: Node()
    '''
    return Node(name, inventory)
