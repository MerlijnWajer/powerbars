#!/usr/bin/env python2

from __future__ import print_function

from flask import Flask, request, abort, render_template
app = Flask(__name__)
app.debug = False

from barconfig import bars, groups, groups_state, presets

import json
import time

hack_time = time.time() - 120.

ALLOW_GET = False  # True to allow GET requests
IGNORE_REFCOUNT = True


class InputException(Exception):
    pass


def get_state(request):
    if 'state' in request.form:
        if request.form['state'] == 'On':
            return True
        elif request.form['state'] == 'Off':
            return False

    raise InputException('')


def group_set_state(group, socket, state):
    if state:
        if group not in socket.refcount:
            socket.refcount.append(group)
        socket.set_state(state)
    else:
        if group in socket.refcount:
            socket.refcount.remove(group)

        if IGNORE_REFCOUNT or len(socket.refcount) == 0:
            socket.set_state(state)


def flip_state(state_dict, key, state):
    if state_dict[key] is None:
        state_dict[key] = state
        return True

    if state_dict[key]:
        if state:
            return True
        else:
            state_dict[key] = False
            return True
    else:
        if state:
            state_dict[key] = True
            return True
        else:
            return True
    return False


def hack_reset_bars():
    # XXX: Hackety-hack.
    global hack_time
    if time.time() - hack_time > 120.:
        hack_time = time.time()
        for bar in bars:
            if hasattr(bar, 'reset_bar'):
                bar.reset_bar()


def print_state():
    s = ""
    for bar in bars:
        for socket in bar.sockets.values():
            s += '%s is at count: %s\n' % (socket.name, str(socket.refcount))

    for k, v in groups_state.iteritems():
        s += '%s: %s\n' % (k, str(v))

    print(s)
    return s


@app.route("/")
def index():
    return render_template('main-nojs.html', bars=bars, groups=groups,
                           presets=presets, filter=filter,
                           sort=lambda y: sorted(y, key=lambda x: x.name),
                           socketfilter=lambda x:
                           not x.name.startswith('Socket'))


@app.route("/alt")
def alt():
    return render_template('alt.html')


@app.route('/all', methods=['GET'])
def all():
    b = {}
    if request.method == 'GET':
        for bar in xrange(len(bars)):
            states = []
            for socket in bars[bar].sockets.values():
                states.append((str(socket), str(socket.state)))
            b[bar] = states
        return json.dumps(b)


@app.route("/<bar>/<port>", methods=['POST'])
#@app.route("/<bar>/<port>", methods=['GET', 'POST'])
def powerbar_iname_pname(bar, port):
    for idx, b in enumerate(bars):
        if b.name == bar:
            for socket in b.sockets.values():
                if socket.name == port:
                    state = get_state(request)

                    hack_reset_bars()
                    socket.set_state(state)

                    if 'echo' in request.form and request.form['echo'].lower() == 'off':
                        return 'Yes'

                    return render_template('main-nojs.html', bars=bars,
                                           groups=groups,
                                           presets=presets, filter=filter,
                                           sort=lambda y: sorted(
                                               y, key=lambda x: x.name),
                                           socketfilter=lambda x: not
                                           x.name.startswith('Socket'),
                                           msg="Bar: %s, Port %s\n" %
                                           (bar, port))
    return "No such bar plus port"


@app.route("/group/<group>", methods=['GET', 'POST'])
def powerbar_g(group):
    if request.method == 'GET':
        states = []
        for socket in groups[group]:
            states.append((str(socket), str(socket.state)))
        return json.dumps(states)
    else:
        state = get_state(request)

        if group not in groups:
            return 'Invalid group'  # TODO: Error code

        hack_reset_bars()

        if flip_state(groups_state, group, state):
            for socket in groups[group]:
                group_set_state(group, socket, state)

        if 'echo' in request.form and request.form['echo'].lower() == 'off':
            return 'Yes'


        # return render_template('status_back.html', msg='%s is %s' % (group,
        #                       'On' if state else 'Off'))
        return render_template('main-nojs.html', bars=bars, groups=groups,
                               presets=presets, filter=filter,
                               sort=lambda y: sorted(y, key=lambda x: x.name),
                               socketfilter=lambda x: not
                               x.name.startswith('Socket'),
                               msg='%s is %s' %
                               (group, 'On' if state else 'Off'))


@app.route("/keepactive", methods=['GET'])
def keepactive():
    global hack_time
    hack_time = time.time()
    for bar in bars:
        if hasattr(bar, 'reset_bar'):
            bar.reset_bar()

    return 'Success'


@app.route("/preset/<preset>", methods=['GET', 'POST'])
def powerbar_p(preset):
    if preset not in presets:
        return 'Invalid preset'  # TODO: Error code

    hack_reset_bars()

    for state in presets[preset]:
        state = state == 'On'
        for group in presets[preset]['On' if state else 'Off']:
            if flip_state(groups_state, group, state):
                for socket in groups[group]:
                    group_set_state(group, socket, state)


    # return render_template('status_back.html',
    #        msg='Prefix is %s' % preset)

    if 'echo' in request.form and request.form['echo'].lower() == 'off':
        return 'Yes'

    return render_template('main-nojs.html', bars=bars, groups=groups,
                           presets=presets, filter=filter,
                           sort=lambda y: sorted(y, key=lambda x: x.name),
                           socketfilter=lambda x: not
                           x.name.startswith('Socket'),
                           msg='Prefix is %s' % preset)


from reset import resetserial
RESET = True

from bar import BayTechPowerBar

if __name__ == "__main__":
    if RESET:
        for bar in bars:
            # XXX: reset_bar here makes sure we've read everything from the bar
            # so it doesn't return bogus on the next read.
            # resetserial() actually resets certain configs in the bar
            if isinstance(bar, BayTechPowerBar):
                bar.reset_bar()
                print('Resetting:', bar.s.port)
                resetserial(bar.s.port)

    app.run(host='::', port=5000)
    #app.run(host='::', port=5000, debug=True)
    # app.run(host='0.0.0.0')
