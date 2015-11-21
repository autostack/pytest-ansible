#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import ansible
import ansible.constants as C
from ansible.runner import Runner
from ansible import playbook
from ansible import callbacks

from pytest_ansible.errors import AnsibleCompoundException
from pytest_ansible.node import get_node

from pkg_resources import parse_version

has_ansible_become = \
    parse_version(ansible.__version__) >= parse_version('1.9.0')


class AnsibleRunnerCallback(callbacks.DefaultRunnerCallbacks):
    '''
    TODO:
    - handle logs
    '''
    def on_ok(self, host, res):
        get_node(host, self.runner.inventory).dispatch(**res)
        super(AnsibleRunnerCallback, self).on_ok(host, res)

    def on_async_ok(self, host, res, jid):
        get_node(host, self.runner.inventory).dispatch(**res)
        super(AnsibleRunnerCallback, self).on_async_ok(host, res, jid)


class AnsibleModule(object):
    '''
    Basic class for reference object's attributes
    to Ansible commands
    '''
    def __init__(self, inventory_manager, pattern='*', **kwargs):
        self.options = kwargs
        # self.inventory = inventory
        self.inventory_manager = inventory_manager
        self.pattern = pattern
        self.options.update([('inventory_manager', inventory_manager),
                             ('pattern', pattern)])

        self.module_name = self.options.get('module_name', None)

    def __getattr__(self, name):
        self.options.update([('module_name', name)])
        return AnsibleModule(**self.options)

    def __call__(self, *args, **kwargs):
        '''
        Adhoc execution wrapper
        :param args: module arguments
        :param kwargs:
         kwargs[run_async]: Running async
         kwargs[time_limit]: related to async
         kwargs[forks]: amount of parallel processes
         kwargs[remote_user]: costume remote user login
         kwargs[remote_pass]: costume remote user password
         kwargs[remote_port]: costume remote port
         kwargs[transport]: support "ssh, paramiko, local"
         kwargs[become_user]: connect as sudo user
         kwargs[become_method]: set to ‘sudo’/’su’/’pbrun’/’pfexec’/’doas’
        :return: Future object in case of async, result dict in case of sync
        '''
        # Assemble module argument string
        module_args = list()
        if args:
            module_args += list(args)
        module_args = ' '.join(module_args)

        # pop async parameters
        async = kwargs.pop('run_async', False)
        time_limit = kwargs.pop('time_limit', 60)

        # Build module runner object
        kwargs = dict(
            inventory=self.inventory_manager,
            pattern=self.pattern,
            callbacks=AnsibleRunnerCallback(),
            module_name=self.module_name,
            module_args=module_args,
            complex_args=kwargs,
            forks=kwargs.pop('forks', C.DEFAULT_FORKS),
            remote_user=kwargs.pop('remote_user', C.DEFAULT_REMOTE_USER),
            remote_pass=kwargs.pop('remote_pass', C.DEFAULT_REMOTE_PASS),
            remote_port=kwargs.pop('remote_port', None),
            transport=kwargs.pop('connection', C.DEFAULT_TRANSPORT),
        )

        if 'become_user' in kwargs:
            # Handle >= 1.9.0 options
            if has_ansible_become:
                kwargs.update(dict(
                    become=True,
                    become_method=kwargs.pop('become_method', C.DEFAULT_BECOME_METHOD),
                    become_user=kwargs.pop('become_user', C.DEFAULT_BECOME_USER)
                ))
            else:
                kwargs.update(dict(
                    sudo=True,
                    sudo_user=kwargs.pop('become_user', C.DEFAULT_BECOME_USER))
                )

        runner = Runner(**kwargs)

        # Run the module
        if async:
            res, poll = runner.run_async(time_limit=time_limit)
            return _ExtendedPoll(res, poll)
        else:
            return _ExtendedPoll(runner.run(), None).poll()


class AnsibleGroup(AnsibleModule):
    def __init__(self, nodes, **kwargs):
        '''
        Wrap AnsibleModule to handle multiple nodes
        :param nodes: Node object
        :param kwargs:
        :return:
        '''
        inventory = nodes[0].inventory
        pattern = ':'.join([host.name for host in nodes])
        super(AnsibleGroup, self).__init__(
            inventory_manager=inventory, pattern=pattern, **kwargs)


class AnsiblePlaybook(AnsibleGroup):
    # TODO: add more playbook validations and configurations
    def run(self, pb_path):
        # Make sure we aggregate the stats
        stats = callbacks.AggregateStats()
        playbook_cb = callbacks.PlaybookCallbacks(
            verbose=ansible.utils.VERBOSITY)

        # TODO: add forks=int
        pb = playbook.PlayBook(
            playbook=pb_path,
            callbacks=playbook_cb,
            runner_callbacks=AnsibleRunnerCallback(),
            inventory=self.inventory_manager,
            stats=stats
        )
        return pb.run()


class _ExtendedPoll(object):
    def __init__(self, result, poller):
        self.__res = result
        self.__poll = poller

    def __getattr__(self, name):
        return getattr(self.__poll, name)

    def __expose_failure(self):
        is_failur = all((res.get('failed', False) or res.get('rc', 0) != 0
                         for host, res in self.__res['contacted'].iteritems()))
        if is_failur or self.__res['dark']:
            raise AnsibleCompoundException(
                'Some of the hosts had failed', **self.__res)

        return self.__res['contacted']

    def poll(self):
        if hasattr(self.__poll, 'poll'):
            return self.__poll.poll()
        else:
            return self.__expose_failure()

    def wait(self, seconds, poll_interval):
        self.__res = self.__poll.wait(seconds, poll_interval)
        return self.__expose_failure()
