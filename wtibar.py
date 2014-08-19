#!/usr/bin/env python3

from __future__ import print_function

from telnetlib import Telnet

from vbar import VirtualPowerSocket, VirtualPowerBar

TIMEOUT = 5. # Quite high; but this is a lot more stable.

class WTIPowerBar(VirtualPowerBar):
    def __init__(self, host='10.0.0.80', name='WTIPowerBar'):
        VirtualPowerBar.__init__(self, name)
        self.host = host


    def make_socket(self, name, ident):
        return WTIPowerSocket(self, name, ident)


class WTIPowerSocket(VirtualPowerSocket):

    def __init__(self, bar, name, ident):
        VirtualPowerSocket.__init__(self, bar, name, ident)


    def set_state(self, state):
        s = 'On' if state else 'Off'

        tel = Telnet(self.bar.host)

        try:
            w = "/%s %d" % (s, self.ident)
            msg = w.encode('ascii') + b"\r\n"
            print("Writing:", repr(msg))
            tel.write(msg)

            print("Reading:", repr(tel.read_until("NPS>")))

            self.state = state
        finally:
            tel.close()
