#!/usr/bin/env python
from __future__ import print_function
from select import select
from os.path import join
from time import sleep
from subprocess import Popen, check_call
from signal import signal, SIGCHLD, SIG_IGN

signal(SIGCHLD, SIG_IGN)
devnull = open('/dev/null', 'w+')

base = '/sys/class/gpio/'
powerbar = 'http://powerbar.ti:5000'

file_spec = {
    'gpio1_ph20/': (1, 'On', '/group/lighteast'),
    'gpio2_ph21/': (1, 'Off', '/group/lighteast'),
    'gpio3_ph22/': (2, 'On', '/group/lightwest'),
    'gpio6_ph25/': (2, 'Off', '/group/lightwest'),
    'gpio5_ph24/': (3, 'On', '/group/power'),
    'gpio7_ph26/': (3, 'Off', '/group/power'),
    'gpio8_ph27/': (4, 'On', '/group/audio'),
    'gpio4_ph23/': (4, 'Off', '/group/audio'),
}

file_state = dict(map(lambda k: (k, 1), file_spec.keys()))
file_fds = dict(map(lambda k: (k, open(join(base, k, 'value'), 'r')),
                    file_spec.keys()))

while True:
    changed = []
    for k, v in file_spec.items():
        fd = file_fds[k]
        fd.seek(0)
        f = int(fd.read().strip())

        if file_state[k] != f:
            changed.append(k)
            print('Changed:', k, v)
            print('Old & New state:', file_state[k], f)

        file_state[k] = f

    for c in changed:
        name, on_off, url = file_spec[c]
        args = ['curl', powerbar + url, '-d', 'state=' + on_off]
        Popen(args, stdout=devnull, stderr=devnull, close_fds=True)

    sleep(0.2)
