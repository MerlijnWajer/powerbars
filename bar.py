#!/usr/bin/env python3

from __future__ import print_function

import time

from vbar import VirtualPowerBar, VirtualPowerSocket

VIRTUAL = False

if not VIRTUAL:
    try:
        from serial import Serial
    except ImportError as e:
        print('Could not import serial. Trying to continue', e)
else:
    print('WARNING: Virtual mode activated')

    class Serial(object):

        def __init__(self, **kwargs):
            pass

        def __getattr__(self, attr):
            return lambda self, **kwargs: None


def write_read(s, m):
    s.write(m)
    s.timeout = 2
    l = len(m) + len('RPC-28A>\r')
    t1 = time.time()
    f = s.read(l)
    return f


class BayTechPowerBar(VirtualPowerBar):

    def __init__(self, path, name='Default PowerBar name'):
        VirtualPowerBar.__init__(self, name)

        s = Serial(port=path, baudrate=9600)

        # Just in case
        s.setDsrDtr(False)
        s.setRtsCts(False)
        s.setXonXoff(False)

        self.s = s

    def make_socket(self, name, ident):
        return BayTechPowerSocket(self, name, ident)

    def reset_bar(self, timeout=2):
        self.s.timeout = timeout
        self.s.write('\r\n')
        m = self.s.read(1000)
        print('Reset read:', m)
        return True


class BayTechPowerSocket(VirtualPowerSocket):

    def __init__(self, bar, name, ident):
        VirtualPowerSocket.__init__(self, bar, name, ident)

    def set_state(self, state):
        s = 'On' if state else 'Off'
        self.state = state
        #print('Setting', self.name, 'to', s)
        m = '%s %d\r\n' % (s, self.ident)
        #print('Writing:', repr(m))
        r = write_read(self.bar.s, m)
        #print('Read:', repr(r))
