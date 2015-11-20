#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# import jinja2
import ansible
# import pytest
import ansible.constants as C

from ansible.inventory import Inventory
from ansible.runner import Runner
from ansible import callbacks

from pytest_ansible.errors import AnsibleCompoundException
from pytest_ansible.node import get_node

from pkg_resources import parse_version
# from tempfile import NamedTemporaryFile


has_ansible_become = \
    parse_version(ansible.__version__) >= parse_version('1.9.0')


class AnsibleRunnerCallback(callbacks.DefaultRunnerCallbacks):
    '''
    TODO:
    - handle logs
    '''
    def on_ok(self, host, res):
        get_node(host, self.runner.inventory).load(res)
        print('Loading on_ok', get_node(host, self.runner.inventory), res)
        super(AnsibleRunnerCallback, self).on_ok(host, res)

    def on_async_ok(self, host, res, jid):
        get_node(host, self.runner.inventory).load(res)
        print('Loading on_async_ok', get_node(host, self.runner.inventory), res)
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
        # Assemble module argument string
        module_args = list()
        if args:
            module_args += list(args)
        module_args = ' '.join(module_args)

        # pop async parameters
        async = kwargs.pop('run_async', False)
        time_limit = kwargs.pop('time_limit', 60)
        forks = kwargs.pop('forks', C.DEFAULT_FORKS)

        # DEBUG
        # print self.inventory_manager
        # print dir(self.inventory_manager)
        # lhost = self.inventory_manager.get_host('127.0.0.1')
        # lhost.set_variable('ansible_ssh_user', 'avi')
        # lhost.set_variable('foo', 'bla')
        # print lhost.vars

        # Build module runner object
        kwargs = dict(
            inventory=self.inventory_manager,
            pattern=self.pattern,
            callbacks=AnsibleRunnerCallback(),
            module_name=self.module_name,
            module_args=module_args,
            complex_args=kwargs,
            forks=forks,
            # remote_user='root',
            # remote_pass='smartvm',
        )

        # Handle >= 1.9.0 options
        # if has_ansible_become:
        #     kwargs.update(dict(
        #         become=self.options.get('become'),
        #         become_method=self.options.get('become_method'),
        #         become_user=self.options.get('become_user'),)
        #     )
        # else:
        #     kwargs.update(dict(
        #         sudo=self.options.get('sudo'),
        #         sudo_user=self.options.get('sudo_user'),)
        #     )

        runner = Runner(**kwargs)
        # return runner.run()

        # Run the module
        if async:
            res, poll = runner.run_async(time_limit=time_limit)
            return _ExtendedPoller(res, poll)
        else:
            return _ExtendedPoller(runner.run(), None).poll()

    def run_playbook(self, env, playbook=None):
        '''
        load playbook by priority
        1 - from script: ansible.run_playbook('test.yml')
        2 - from mark: @pytest.mark.ansible(playbook='test.yml')
        3 - from cli: py.test --ansible-playbook test.yml
        '''

        playbook = playbook or self.options.get('playbook')

        # Make sure we aggregate the stats
        stats = callbacks.AggregateStats()
        playbook_cb = callbacks.PlaybookCallbacks(
            verbose=ansible.utils.VERBOSITY)

        # TODO: add forks=int
        pb = ansible.playbook.PlayBook(
            playbook=playbook,
            callbacks=playbook_cb,
            runner_callbacks=AnsibleRunnerCallback(),
            inventory=self.inventory_manager,
            stats=stats
        )
        return pb.run()


class AnsibleGroup(AnsibleModule):
    def __init__(self, nodes, **kwargs):
        inventory = nodes[0].inventory
        pattern = ':'.join([host.name for host in nodes])
        super(AnsibleGroup, self).__init__(
            inventory_manager=inventory, pattern=pattern, **kwargs)


class _ExtendedPoller(object):
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


# class AnsibleHost(AnsibleModule):
#     '''
#     '''
#     INVENTORY_TEMPLATE='''
# [host]
# {{ip_address}}
# [host:vars]
# {{host_vars}}
# '''
#
#     def __init__(self, host, **kwargs):
#         '''
#         Initialise Ansible host wrapper
#         :param host: ansible host object
#         '''
#         try:
#             # render inventory per host
#             inventory_template = jinja2.Template(self.INVENTORY_TEMPLATE)
#             rendered_inventory = inventory_template.render(
#                 dict(ip_address=host.name,
#                      host_vars='\n'.join(['{}={}'.format(k, v)
#                                           for k, v in host.vars.iteritems()])))
#
#             # Generate temporary inventory
#             temp = NamedTemporaryFile(delete=False)
#             temp.write(rendered_inventory)
#             temp.close()
#
#             # load inventory from temporary file
#             i_m = ansible.inventory.Inventory(temp.name)
#         except Exception as err:
#             raise pytest.UsageError("Failed to initiate inventory!, "
#                                     "error: {0}".format(err))
#
#         super(AnsibleHost, self).__init__(
#             inventory_manager=i_m, pattern='*', **kwargs)

if __name__ == '__main__':
    i = Inventory('../inventory1.yaml')
    mod = AnsibleModule(inventory_manager=i, pattern='127.0.0.1')
    print mod
    print mod.ping()
    print mod.shell('pwd')
