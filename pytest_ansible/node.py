#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pytest_ansible.utils import memoize


# class Node(AnsibleHost):
#     def __init__(self, host, **kwargs):
#         super(Node, self).__init__(host=host, **kwargs)
#         self._host = host
#
#     def __getattr__(self, item):
#         try:
#             return getattr(self._host, item)
#         except AttributeError:
#             return super(Node, self).__getattr__(item)
#
#     def foo(self):
#         return 'AAAAAAAA'


class Node(object):
    def __init__(self, name, inventory):
        self._name = name
        self._inventory = inventory
        self.res = None

    @property
    def vars(self):
        return self.inventory.get_host(self._name).vars

    @property
    def name(self):
        return self._name

    @property
    def ipv4_address(self):
        return self.inventory.get_host(self._name).ipv4_address

    @property
    def inventory(self):
        return self._inventory

    def load(self, res):
        # FIXME: this is just a poc for loading results
        self.res = res


@memoize
def get_node(name, inventory):
    '''
    Generating Node object base on given ansible host instance
    :param name: host name
    :param inventory: inventory manager instance
    :param kwargs: set of dynamic attributes input by CLI or markers
    :return: Node()
    '''
    return Node(name, inventory)
