#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import yaml

from pytest_ansible.nodes import Node

__author__ = 'Avi Tal <avi3tal@gmail.com>'
__date__ = 'Sep 3, 2015'


class Compound(list):
    '''
    '''
    def __call__(self, *args, **kwargs):
        # TODO: run in parallel
        return Compound([child(*args, **kwargs) for child in self])

    def __getattr__(self, item):
        return Compound([getattr(child, item)
                         for child in super(Compound, self).__iter__()])

    def __delattr__(self, item):
        [delattr(child, item) for child in self]

    def __setattr__(self, item, value):
        [setattr(child, item, value)
         for child in super(Compound, self).__iter__()]

    def __getslice__(self, i, j):
        slice_iter = super(Compound, self).__getslice__(i, j)
        return Compound(slice_iter)

    def __add__(self, y):
        iterable = super(Compound, self).__add__(y)
        return Compound(iterable)

    def __sub__(self, other):
        iterable = [item for item in self if item not in other]
        return Compound(iterable)

    def filter(self, key, value):
        sub = []
        for child in self:
            try:
                if getattr(child, key) == value:
                    sub.append(child)
            except AttributeError:
                continue
        return Compound(sub)

#    def filter(self, **kwargs):
#        return Compound([self._filter(k, v) for k, v in kwargs.iteritems()])


class _Environment(dict):
    @property
    def all(self):
        all_set = set()
        for _, hosts in self.iteritems():
            all_set |= set(hosts)
        return Compound(all_set)

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            return super(_Environment, self).__getattribute__(item)


def initialize_environment(request):
    _ctx = _Environment()
    with open(request.config.getvalue('inventory'), 'r') as f:
        data = yaml.load(f)
    for grp, hosts in data.iteritems():
        # FIXME: parse and load only relevant groups
        _ctx[grp] = Compound([Node(**kw) for kw in hosts])

    return _ctx
