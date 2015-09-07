#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = 'Avi Tal <avi3tal@gmail.com>'
__date__ = 'Sep 3, 2015'


class Facts(dict):
    PREF = 'ansible_'

    def __getattr__(self, attr):
        try:
            data = self[attr]
            if isinstance(data, dict):
                data = Facts(data)
            return data
        except KeyError:
            if attr.startswith(self.PREF):
                raise
            attr = '{}{}'.format(self.PREF, attr)
            return getattr(self, attr)


class Node(object):
    def __init__(self, address, **kwargs):
        self.connection = kwargs.get('connection', 'smart')
        self.user = kwargs.get('user', 'root')

        self.address = address
        self._setup = None

    def __repr__(self):
        repr_template = ("<{0.__class__.__module__}.{0.__class__.__name__}"
                         "object at {1} | node ip {2}>")
        return repr_template.format(self, hex(id(self)), self.address)

    @property
    def stripe(self):
        return '{ip} connection={conn} ansible_ssh_user={user}'.format(
            ip=self.address, conn=self.connection, user=self.user)

    @property
    def setup(self):
        return self._setup

    @setup.setter
    def setup(self, data):
        # TODO: handle "changed" flags
        self._setup = Facts(data['ansible_facts'])
