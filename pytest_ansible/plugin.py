#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import ansible
import os
import pytest
import ansible.constants as C

from pytest_ansible.environment import initialize_environment
from pytest_ansible.actions import (initialize_ansible, has_ansible_become)
from pytest_ansible.redisq import RedisQueue
from pytest_ansible.dispatcher import Dispatcher

from uuid import uuid4

__author__ = 'Avi Tal <avi3tal@gmail.com>'
__date__ = 'Sep 1, 2015'


def pytest_addoption(parser):
    '''Add options to control ansible.'''

    group = parser.getgroup('pytest-infra')
    group.addoption('--inventory',
                    default=None,
                    action='store',
                    help='Inventory file URI (default: %default)')
    group.addoption('--ansible-playbook',
                    action='store',
                    dest='ansible_playbook',
                    default=None,
                    metavar='ANSIBLE_PLAYBOOK',
                    help='ansible playbook file URI (default: %default)')
    group.addoption('--ansible-connection',
                    action='store',
                    dest='ansible_connection',
                    default=C.DEFAULT_TRANSPORT,
                    help="connection type to use (default: %default)")
    group.addoption('--ansible-user',
                    action='store',
                    dest='ansible_user',
                    default=C.DEFAULT_REMOTE_USER,
                    help='connect as this user (default: %default)')
    group.addoption('--ansible-debug',
                    action='store_true',
                    dest='ansible_debug',
                    default=False,
                    help='enable ansible connection debugging')

    # classic privilege escalation
    group.addoption('--ansible-sudo',
                    action='store_true',
                    dest='ansible_sudo',
                    default=C.DEFAULT_SUDO,
                    help="run operations with sudo [nopasswd] "
                    "(default: %default) (deprecated, use become)")
    group.addoption('--ansible-sudo-user',
                    action='store',
                    dest='ansible_sudo_user',
                    default='root',
                    help="desired sudo user (default: %default) "
                    "(deprecated, use become)")

    if has_ansible_become:
        # consolidated privilege escalation
        group.addoption('--ansible-become',
                        action='store_true',
                        dest='ansible_become',
                        default=C.DEFAULT_BECOME,
                        help="run operations with become, "
                        "nopasswd implied (default: %default)")
        group.addoption('--ansible-become-method',
                        action='store',
                        dest='ansible_become_method',
                        default=C.DEFAULT_BECOME_METHOD,
                        help="privilege escalation method to use "
                        "(default: %%default), valid "
                        "choices: [ %s ]" % (' | '.join(C.BECOME_METHODS)))
        group.addoption('--ansible-become-user',
                        action='store',
                        dest='ansible_become_user',
                        default=C.DEFAULT_BECOME_USER,
                        help='run operations as this user (default: %default)')


def pytest_configure(config):
    '''
    Maybe could be for deployment period
    '''
    if config.getvalue('ansible_debug'):
        ansible.utils.VERBOSITY = 5


def _verify_inventory(config):
    # TODO: add yaml validation
    _inventory = config.getvalue('inventory')
    try:
        return os.path.exists(_inventory)
    except:
        return False


def pytest_collection_modifyitems(session, config, items):
    uses_infra_fixtures = False
    for item in items:
        try:
            if any([fixture == 'env' for fixture in item.fixturenames]):
                uses_infra_fixtures = True
                break
        except AttributeError:
            continue

    if uses_infra_fixtures:
        errors = []
        if not _verify_inventory(config):
            errors.append("Unable to load an inventory file, "
                          "specify one with the --inventory parameter.")

        if errors:
            raise pytest.UsageError(*errors)


def pytest_report_header(config):
    '''
    Include the version of infrastructure in the report header
    '''
    return 'Infrastructure version ...'


@pytest.yield_fixture(scope='session')
def env(request):
    '''
    Return Environment instance with function scope.
    '''
    yield initialize_environment(request)


@pytest.yield_fixture(scope='session')
def ansible(request, env):
    '''
    Return _AnsibleModule instance with function scope.
    '''
    queue = RedisQueue(str(uuid4()))
    consumer = Dispatcher(queue, env)
    consumer.start()
    yield initialize_ansible(request, queue)
    queue.put('quit')
    consumer.join()