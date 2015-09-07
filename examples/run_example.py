#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import time

from pytest_infra.redisq import RedisQueue

from fib import slow_fib


__author__ = 'Avi Tal <avi3tal@gmail.com>'
__date__ = 'Sep 6, 2015'


def main():
    # Range of Fibonacci numbers to compute
    fib_range = range(20, 34)

    # Kick off the tasks asynchronously
    q = RedisQueue('test1')
    i = 0
    for x in fib_range:
        q.put(slow_fib(x))
        i += 1
    q = RedisQueue('test')
    start_time = time.time()
    while i:
        os.system('clear')
        print('Asynchronously: (now = %.2f)' % (time.time() - start_time,))
        for x in fib_range:
            result = q.get_nowait()
            if result is None:
                result = '(calculating)'
            else:
                i -= 1
            print('fib(%d) = %s' % (x, result))
        print('')
        print('To start the actual in the background, run a worker:')
        print('    python examples/run_worker.py')
        time.sleep(0.2)

    print('Done')


if __name__ == '__main__':
    # Tell RQ what Redis connection to use
    main()
