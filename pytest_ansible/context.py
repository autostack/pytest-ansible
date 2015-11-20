#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pytest
import ansible
from pytest_ansible.node import get_node
from pytest_ansible.wrappers import AnsibleGroup
from ansible.inventory import Inventory


class GroupDispatch(list):

    def __call__(self, *args, **kwargs):
        return GroupDispatch([child(*args, **kwargs) for child in self])

    def __getattr__(self, item):
        try:
            _list = [getattr(child, item) for child in self]
            if len(_list) > 1:
                return GroupDispatch(_list)
            return _list[0]
        except AttributeError:
            return AnsibleGroup(self, module_name=item)

    def __delattr__(self, item):
        [delattr(child, item) for child in super(GroupDispatch, self).__iter__()]

    def __setattr__(self, item, value):
        [setattr(child, item, value)
         for child in super(GroupDispatch, self).__iter__()]

    def __getslice__(self, i, j):
        slice_iter = super(GroupDispatch, self).__getslice__(i, j)
        return GroupDispatch(slice_iter)

    def __getitem__(self, item):
        item = super(GroupDispatch, self).__getitem__(item)
        return GroupDispatch([item])

    # def __add__(self, y):
    #     iterable = super(AnsibleGroup, self).__add__(y)
    #     return AnsibleGroup(iterable)

    def __sub__(self, other):
        iterable = [item for item in self if item not in other]
        return GroupDispatch(iterable)

    def _filter(self, nodes, key, value):
        sub = []
        for child in nodes:
            try:
                if getattr(child, key) == value:
                    sub.append(child)
            except AttributeError:
                continue
        return GroupDispatch(sub)

    def filter(self, **kwargs):
        ''' Filter, support only AND mode '''
        nodes = self
        for k, v in kwargs.iteritems():
            nodes = self._filter(nodes, k, v)
        return nodes


class Context(dict):
    '''
    Read inventory and split groups to keys
    initiate each host and identify type using class_type
    '''
    def __init__(self, inventory, *args, **kwargs):
        super(Context, self).__init__(*args, **kwargs)
        self.inventory = inventory

    def __getattr__(self, item):
        return self[item]

    def __setitem__(self, key, value):
        super(Context, self).__setitem__(key, GroupDispatch(value))


def load_context(inventory):
    try:
        inventory_manager = Inventory(host_list=inventory)
    except ansible.errors.AnsibleError as e:
        raise pytest.UsageError(e)

    ctx = Context(inventory_manager)

    for grp in inventory_manager.get_groups():
        hosts = grp.get_hosts()
        if not hosts:
            continue
        ctx[grp.name] = [get_node(host.name, inventory_manager) for host in hosts]

    return ctx


if __name__ == '__main__':
    _ctx = load_context('../inventory1.yaml')
    # print _ctx
    # for n in _ctx.nodes:
    #     print n.name, n
    # print _ctx.nodes.command('pwd')
    a = _ctx.nodes[-1].command('uptime', run_async=True)
    print('BEFORE', _ctx.nodes[-1].res)
    # print _ctx.nodes.vars
    print(a.wait(10, 1))
    print('AFTER', _ctx.nodes[-1].res)