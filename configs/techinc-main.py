#!/usr/bin/env python3

from __future__ import print_function

from bar import BayTechPowerBar
from httpbar import HTTPPowerBar

# This is the main config for TechInc (http://techinc.nl)
# The config for the other bar can be found in configs/techinc-west.py

bars = []

FIRST_BAR = BayTechPowerBar('/dev/ttyS0', name='MLP')
AUX_BAR = HTTPPowerBar(host='http://10.0.20.41:5000', name='AUX')

bars += [
    FIRST_BAR,
    AUX_BAR
]

def make_bar(bar, name, ident=None):
    if ident is None:
        ident = name

    __s = bar.make_socket(name, ident)
    globals()[name] = __s
    bar.sockets[name] = __s

# Bar 1

make_bar(FIRST_BAR, 'LIGHT_MAKERLANE', 3)
make_bar(FIRST_BAR, 'LIGHT_MAKERTABLE', 4)
make_bar(FIRST_BAR, 'LIGHT_TABLE', 5)
make_bar(FIRST_BAR, 'LIGHT_CRAFT', 6)
make_bar(FIRST_BAR, 'LIGHT_ENTRANCE', 7)
make_bar(FIRST_BAR, 'LIGHT_KITCHEN', 8)
make_bar(FIRST_BAR, 'LIGHT_WHEEL', 9)
make_bar(FIRST_BAR, 'LIGHT_SOFA', 10)

make_bar(FIRST_BAR, 'AUDIO_AMPLIFIER', 13)
make_bar(FIRST_BAR, 'AUDIO_MIXER', 14)

make_bar(FIRST_BAR, 'MONITOR_3D_1', 16)
make_bar(FIRST_BAR, 'MONITOR_3D_2', 17)

make_bar(FIRST_BAR, 'PRINTER', 18)
make_bar(FIRST_BAR, 'MONITOR_AV_1', 19)
make_bar(FIRST_BAR, 'MONITOR_AV_2', 20)

make_bar(AUX_BAR, 'W_POWER_NW_TABLE')
make_bar(AUX_BAR, 'W_POWER_SW_TABLE')
make_bar(AUX_BAR, 'W_POWER_MAIN_TABLE')
make_bar(AUX_BAR, 'W_POWER_PILLAR')

make_bar(AUX_BAR, 'W_AIR_FAN')

make_bar(AUX_BAR, 'W_LIGHT_TABLE')
make_bar(AUX_BAR, 'W_LIGHT_TL_DOOR')
make_bar(AUX_BAR, 'W_LIGHT_SOLDER')
make_bar(AUX_BAR, 'W_LIGHT_THEATER')
make_bar(AUX_BAR, 'W_LIGHT_GLASS')


groups = {
    'general' : [LIGHT_ENTRANCE, LIGHT_KITCHEN, LIGHT_SOFA, LIGHT_TABLE, LIGHT_WHEEL],
    'craft'   : [LIGHT_CRAFT],
    'audio' : [AUDIO_AMPLIFIER, AUDIO_MIXER],
    'displays' : [MONITOR_AV_1, MONITOR_AV_2, MONITOR_3D_1, MONITOR_3D_2],
    'av' : [MONITOR_AV_1, MONITOR_AV_2],

    'soldering' : [W_POWER_NW_TABLE, W_POWER_SW_TABLE, W_LIGHT_SOLDER],
    'powerwest' : [W_POWER_NW_TABLE, W_POWER_MAIN_TABLE, W_POWER_SW_TABLE, W_POWER_PILLAR],
    'lightwest' : [W_LIGHT_TABLE, W_LIGHT_THEATER, W_LIGHT_GLASS, W_LIGHT_SOLDER],
    'tlwest'    : [W_LIGHT_TL_DOOR],
    'makerlane' : [LIGHT_MAKERLANE, LIGHT_MAKERTABLE, MONITOR_3D_1,
                   MONITOR_3D_2],
    'airfan'    : [W_AIR_FAN],
}


groups_state = {}
for _ in groups.keys():
    groups_state[_] = None

GROUPS_LIGHT = ['general', 'makerlane', 'lightwest', 'tlwest', 'craft']

presets = {
    'lightsoff' : {
        'Off' : GROUPS_LIGHT + ['airfan'],
        'On' : [],
    },
    'lightson' : {
        'Off' : [],
        'On' : GROUPS_LIGHT,
    },
    'alloff' :{
        'Off' : list(groups.keys()),
    },
    'allon' :{
        'On' : list(groups.keys()),
    },
}
