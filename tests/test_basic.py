#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import pytest
from pprint import pprint as pp

__author__ = 'Avi Tal <avi3tal@gmail.com>'
__date__ = 'Sep 1, 2015'


def test_ctx(env):
    print
    pp(env)
    l1 = len(env)
    print 'Adding test group'
    env['test'] = []
    print 'env.test >>', env.test
    print 'type(env.test) >>', type(env.test)
    assert len(env) - 1 == l1, 'Length was not increased'

    print 'Deleting test group'
    del env['test']
    l1 = len(env)
    pp(env)
    assert len(env) == l1, 'Length was not increased'


def test_all_attr_exists(env):
    assert hasattr(env, 'all'), 'all attr does not exists'
    assert hasattr(env, 'hosts'), 'hosts attr does not exists'
    env['test'] = []
    assert hasattr(env, 'test'), 'Failed to add new attr'
    del env['test']
    assert not hasattr(env, 'test'), 'Failed to delete new attr'


def test_slice(env):
    print
    pp(env.all[:2])
    pp(env.hosts[1])
    pp(env.all[-1])


def test_ping(env, ansible):
    print
    pp(ansible.ping(env.all))
    pp(ansible.ping(env.all[0]))
    pp(ansible.ping(env.all[:-1]))


def test_hosts_uname(env, ansible):
    print
    future = ansible.command(env.hosts, 'uname -a', run_async=True)
    print 'Future >>> ', future
    pp(future.wait(60, 2))


@pytest.mark.parametrize('playbook', ['/Users/avi/git/pytest-infra/tests/play1.yml'])
def test_play1(env, ansible, playbook):
    print
    pp(ansible.run_playbook(env.hosts, playbook))


def test_facts(env, ansible):
    print
    ansible.setup(env.hosts)
    pp(env)
    pp(env.hosts[1].facts)
#    print env.hosts.facts.default_ipv4.address
    env.set_concrete_os()
    pp(env)
    env.set_concrete_os()
    ansible.setup(env.hosts)
    pp(env)
    print(type(env.hosts[1].facts))
