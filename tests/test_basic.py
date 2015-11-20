#!/usr/bin/ctx python
# -*- coding: UTF-8 -*-

import pytest
from pprint import pprint as pp

__author__ = 'Avi Tal <avi3tal@gmail.com>'
__date__ = 'Sep 1, 2015'


def test_ctx(ctx):
    print
    pp(ctx)


# def test_all_attr_exists(ctx):
#     assert hasattr(ctx, 'all'), 'all attr does not exists'
#     assert hasattr(ctx, 'hosts'), 'hosts attr does not exists'
#     ctx['test'] = []
#     assert hasattr(ctx, 'test'), 'Failed to add new attr'
#     del ctx['test']
#     assert not hasattr(ctx, 'test'), 'Failed to delete new attr'


def test_slice(ctx):
    print
    # pp(ctx.all[:2])
    pp(ctx.nodes[0])
    pp(ctx.all[-1])


def test_ping(ctx):
    print
    pp(ctx.all.ping())
    pp(ctx.all[0].ping())


def test_hosts_uname(ctx):
    print
    future = ctx.nodes.command('uname -a', run_async=True)
    print 'Future >>> ', future
    pp(future.wait(60, 2))


# @pytest.mark.parametrize('playbook', ['/Users/avi/git/pytest-ansible/tests/play1.yml'])
# def test_play1(ctx, run, playbook):
#     print
#     pp(run.run_playbook(ctx.hosts, playbook))
