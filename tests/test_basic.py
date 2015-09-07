#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import pytest
from pprint import pprint as pp

__author__ = 'Avi Tal <avi3tal@gmail.com>'
__date__ = 'Sep 1, 2015'


def test_ctx(env):
    print
    pp(env)
    print env


def test_all(env):
    print
    pp(env.all)
    print env.all


def test_hosts(env):
    print
    pp(env.hosts)
    print env.hosts


def test_slice(env):
    print
    pp(env.all[:2])
    print env.all[:2]


def test_all_ping(env, ansible):
    print
    pp(ansible.ping(env.all))


def test_single_ping(env, ansible):
    print
    pp(ansible.ping(env.all[0]))


def test_hosts_uname(env, ansible):
    print
    future = ansible.command(env.hosts, 'uname -a', run_async=True)
    print '<<<<>>>>', future
    pp(future.wait(60, 2))


@pytest.mark.parametrize('playbook', ['/Users/avi/git/pytest-infra/tests/play1.yml'])
def test_play1(env, ansible, playbook):
    print
    pp(ansible.run_playbook(env.hosts, playbook))


def test_facts(env, ansible):
    print
    ansible.setup(env.hosts[1])
    pp(env.hosts[1].setup)


def test_conn_facts_env(env, ansible):
    print
    ansible.setup(env.hosts)
    print env.hosts.setup.all_ipv4_addresses
