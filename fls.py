# *****************************************************************************
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************
"""playing implementation of a (simple) simulated cryostat

Taken from frappy, this is intended to simulate a cryostat that can be used in
the different demos on the website as a showcase of the different frameworks.

It accepts the following messages:



"""


import argparse
import logging
import random
import signal
import socket
import socketserver
import sys
import threading
import time
from functools import partial
from math import atan
from enum import Enum


MOVE = 'MOV'
STOP = 'STP'
SETPARAM = 'SET'
READ = 'ASK'
ASK_PLACEHOLDER = '?'
all_incoming = (MOVE, STOP, SETPARAM, READ)
ERROR = 'ERR'
ANSWER = 'OUT'


rparams = ('setpoint', 'heaterpower', 'value')
rwparams = ('ramp', 'maxpower', 'p', 'i', 'd', 'mode')
params = rparams + rwparams + ('target',)
LIMITS = {
    'ramp': (0, 1000),
    'maxpower': (0, 2**31),
    'target': (2, 2**31),
    'p': (0, 2**31),
    'i': (0, 100),
    'd': (0, 100),
    'mode': (0, 2),
}


class Op(Enum):
    Read = 'read_'
    Write = 'write_'
    Command = 'call_'


def convert(param, value):
    try:
        v = float(value)
    except ValueError:
        return None
    min, max = LIMITS[param]
    if min <= v <= max:
        return v
    return None


def parse_message(msg):
    """Parse an incoming message.

    Returns a tuple of (OP, *args) if the message is well formed or (None,).
    Format: OP,PARAM,[VALUE|?]
    """
    op, param, val = (msg.split(',', 2) + ['', ''])[0:3]
    # TODO: give an error reason
    if not param or not val:
        return (None,)
    if op == READ:
        if val != ASK_PLACEHOLDER:
            return (None,)
        if param not in params:
            return (None,)
        return (Op.Read, param)
    elif op == MOVE:
        if param != 'target':
            return (None,)
        if not (value := convert(param, val)):
            return (None,)
        return (Op.Write, param, value)
    elif op == SETPARAM:
        if param not in rwparams:
            return (None,)
        if not (value := convert(param, val)):
            return (None,)
        return (Op.Write, param, value)
    elif op == STOP:
        return (Op.Command, 'stop')
    return (None,)


class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        self.sim = self.server.sim
        self.log = self.server.log
        self.log.info('handling connection from %s:%d', *self.client_address)
        self.request.settimeout(1)
        self.running = True
        lock = self.server.lock
        buffer = b''
        while self.running and not self.server.shutdown_started:
            try:
                data = self.request.recv(200)
                if not data:
                    # b'' means socket was closed
                    self.log.info("connection to %s:%d closed", *self.client_address)
                    self.running = False
                    continue
                buffer += data
                self.log.info(buffer)
            except socket.timeout:
                pass
            except socket.error as e:
                self.running = False
                self.log.exception(e)
                # raise ConnectionClose() from e
            if b'\n' not in buffer:
                continue
            message, buffer = buffer.split(b'\n', 1)
            message = message.rstrip(b'\r')
            self.log.info("message: %s", message)
            message = message.decode('utf-8')
            op, *args = parse_message(message)
            self.log.info("op: %s, args: %s", op, args)
            if op is None:
                self.request.sendall(b'ERR,,\r\n')
            if op == Op.Read:
                (param,) = args
                if (func := getattr(self.sim, op.value + param, None)):
                    with lock:
                        value = func()
                    self.request.sendall(f'{ANSWER},{param},{value}\r\n'.encode('utf-8'))
                else:
                    self.request.sendall(b'ERR,,\r\n')
            if op == Op.Write:
                param, value = args
                if (func := getattr(self.sim, op.value + param, None)):
                    with lock:
                        func(value)
                    self.request.sendall(f'{ANSWER},{param},{value}\r\n'.encode('utf-8'))
                else:
                    self.request.sendall(b'ERR,,\r\n')
            if op == Op.Command:
                (param,) = args
                if (func := getattr(self.sim, op.value + param, None)):
                    with lock:
                        value = func()
                    self.request.sendall(f'{ANSWER},{param},{value}\r\n'.encode('utf-8'))
                else:
                    self.request.sendall(b'ERR,,\r\n')


class Server(socketserver.ThreadingTCPServer):
    def __init__(self, server_address, RequestHandlerClass, lock, log, sim, bind_and_activate=True):
        self.lock = lock
        self.log = log
        self.sim = sim
        self.shutdown_started = False
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)


class Interface:
    def __init__(self, port, lock, log, sim):
        self.log = log.getChild('if')
        self.port = port
        self.lock = lock
        self.server = None
        self.sim = sim

    def start(self):
        self._thread = threading.Thread(name='fls-interface', target=self.thread)
        # self._thread.daemon = True
        self._thread.start()

    def thread(self):
        with Server(('', self.port), Handler, self.lock, self.log, self.sim) as server:
            self.server = server
            server.serve_forever()
        self.server = None

    def shutdown(self):
        if self.server:
            self.server.shutdown_started = True
            self.server.server_close()
            self.server.shutdown()
        if self._thread and self._thread.is_alive():
            self._thread.join()


# from frappy.lib
def clamp(_min, value, _max):
    """return the median of 3 values,

    i.e. value if min <= value <= max, else min or max depending on which side
    value lies outside the [min..max] interval. This works even when min > max!
    """
    # return median, i.e. clamp the the value between min and max
    return sorted([_min, value, _max])[1]


class Mode(Enum):
    ramp = 0
    pid = 1
    openloop = 2


# adapted from the frappy cryo demo
class Cryostat:
    """simulated cryostat with:

    - heat capacity of the sample
    - cooling power
    - thermal transfer between regulation and samplen
    """
    # === fixed params ===
    # jitter = Parameter("amount of random noise on readout values",
    #                    datatype=FloatRange(0, 1), unit="K",
    #                    default=0.1, readonly=False, export=False)
    jitter = 0.1
    # T_start = Parameter("starting temperature for simulation",
    #                     datatype=FloatRange(0), default=10,
    #                     export=False)
    T_start = 20
    # looptime = Parameter("timestep for simulation",
    #                      datatype=FloatRange(0.01, 10), unit="s", default=1,
    #                      readonly=False, export=False)
    looptime = 1
    # heater = Parameter("current heater setting",
    #                    datatype=FloatRange(0, 100), default=0, unit="%",
    #                    group='heater_settings')
    heater = 4.1
    # tolerance = Parameter("temperature range for stability checking",
    #                       datatype=FloatRange(0, 100), default=0.1, unit='K',
    #                       readonly=False,
    #                       group='stability')
    tolerance = 0.1
    # window = Parameter("time window for stability checking",
    #                    datatype=FloatRange(1, 900), default=30, unit='s',
    #                    readonly=False,
    #                    group='stability')
    window = 30

    # === readonly ===
    # setpoint = Parameter("current setpoint during ramping else target",
    #                      datatype=FloatRange(), default=1, unit='K')
    setpoint = None
    # heaterpower = Parameter("current heater power",
    #                         datatype=FloatRange(0), default=0, unit="W",
    #                         group='heater_settings')
    heaterpower = None
    # value = TestParameter("regulation temperature",
    #                       datatype=FloatRange(0), default=0, unit="K",
    #                       test='TEST')
    value = None

    # === changeable params ===
    # ramp = Parameter("ramping speed of the setpoint",
    #                  datatype=FloatRange(0, 1e3), unit="K/min", default=1,
    #                  readonly=False)
    ramp = 6
    # maxpower = Parameter("Maximum heater power",
    #                      datatype=FloatRange(0), default=1, unit="W",
    #                      readonly=False,
    #                      group='heater_settings')
    maxpower = 20.0
    # target = Parameter("target temperature",
    #                    datatype=FloatRange(0), default=0, unit="K",
    #                    readonly=False,)
    target = 10.0
    # p = Parameter("regulation coefficient 'p'",
    #               datatype=FloatRange(0), default=40, unit="%/K", readonly=False,
    #               group='pid')
    p = 40
    # i = Parameter("regulation coefficient 'i'",
    #               datatype=FloatRange(0, 100), default=10, readonly=False,
    #               group='pid')
    i = 10
    # d = Parameter("regulation coefficient 'd'",
    #               datatype=FloatRange(0, 100), default=2, readonly=False,
    #               group='pid')
    d = 2
    # mode = Parameter("mode of regulation",
    #                  datatype=EnumType('mode', ramp=None, pid=None, openloop=None),
    #                  default='ramp',
    #                  readonly=False)
    # 0 = ramp, 1 = pid, 2 = openloop
    mode = Mode(0)

    def __init__(self, lock, log):
        self.lock = lock
        self.log = log.getChild('sim')

    def start(self):
        self._stopflag = False
        self._thread = threading.Thread(name='fls-simthread', target=self.thread)
        # self._thread.daemon = True
        self._thread.start()

    # def read_status(self):
    #     # instead of asking a 'Hardware' take the value from the simulation
    #     return self.status

    def read_value(self):
        # return regulation value (averaged regulation temp)
        return self.regulationtemp + \
            self.jitter * (0.5 - random.random())

    def read_target(self):
        return self.target

    def write_target(self, value):
        value = round(value, 2)
        if value == self.target:
            # nothing to do
            return value
        self.target = value
        # next read_status will see this status, until the loop updates it
        # self.status = self.Status.BUSY, 'new target set'
        return value

    def read_heaterpower(self):
        return self.heaterpower

    def read_setpoint(self):
        return self.heaterpower

    def read_ramp(self):
        return self.ramp

    def write_ramp(self, value):
        self.ramp = value

    def read_maxpower(self):
        return self.maxpower

    def write_maxpower(self, newpower):
        # rescale heater setting in % to keep the power
        heat = max(0, min(100, self.heater * self.maxpower / float(newpower)))
        self.heater = heat
        self.maxpower = newpower
        return newpower

    def read_p(self):
        return self.p

    def write_p(self, value):
        self.p = value

    def read_i(self):
        return self.i

    def write_i(self, value):
        self.i = value

    def read_d(self):
        return self.d

    def write_d(self, value):
        self.d = value

    def read_mode(self):
        return self.mode.value

    def write_mode(self, value):
        self.mode = Mode(value)

    def call_stop(self):
        """Stop ramping the setpoint

        by setting the current setpoint as new target"""
        # XXX: discussion: take setpoint or current value ???
        self.write_target(self.setpoint)

    #
    # calculation helpers
    #
    def __coolerPower(self, temp):
        """returns cooling power in W at given temperature"""
        # quadratic up to 42K, is linear from 40W@42K to 100W@600K
        # return clamp((temp-2)**2 / 32., 0., 40.) + temp * 0.1
        return clamp(15 * atan(temp * 0.01)**3, 0., 40.) + temp * 0.1 - 0.2

    def __coolerCP(self, temp):
        """heat capacity of cooler at given temp"""
        return 75 * atan(temp / 50)**2 + 1

    def __heatLink(self, coolertemp, sampletemp):
        """heatflow from sample to cooler. may be negative..."""
        flow = (sampletemp - coolertemp) * \
               ((coolertemp + sampletemp) ** 2) / 400.
        cp = clamp(
            self.__coolerCP(coolertemp) * self.__sampleCP(sampletemp), 1, 10)
        return clamp(flow, -cp, cp)

    def __sampleCP(self, temp):
        return 3 * atan(temp / 30) + \
            12 * temp / ((temp - 12.)**2 + 10) + 0.5

    def __sampleLeak(self, temp):
        return 0.02 / temp

    def thread(self):
        self.sampletemp = self.T_start
        self.regulationtemp = self.T_start
        # self.status = self.Status.IDLE, ''
        while not self._stopflag:
            try:
                self.__sim()
            except Exception as e:
                self.log.exception(e)
                # self.status = self.Status.ERROR, str(e)

    def __sim(self):
        # complex thread handling:
        # a) simulation of cryo (heat flow, thermal masses,....)
        # b) optional PID temperature controller with windup control
        # c) generating status+updated value+ramp
        # this thread is not supposed to exit!

        self.setpoint = self.target
        # local state keeping:
        regulation = self.regulationtemp
        sample = self.sampletemp
        # keep history values for stability check
        window = []
        timestamp = time.time()
        heater = 0
        lastflow = 0
        last_heaters = (0, 0)
        delta = 0
        _I = _D = 0
        lastD = 0
        damper = 1
        lastmode = self.mode
        while not self._stopflag:
            t = time.time()
            h = t - timestamp
            if h < self.looptime / damper:
                time.sleep(clamp(self.looptime / damper - h, 0.1, 60))
                continue
            with self.lock:
                # a)
                sample = self.sampletemp
                regulation = self.regulationtemp
                heater = self.heater

                heatflow = self.__heatLink(regulation, sample)
                # self.log.debug('sample = %.5f, regulation = %.5f, heatflow = %.5g',
                #                sample, regulation, heatflow)
                newsample = max(0, sample + (self.__sampleLeak(sample) - heatflow)
                                / self.__sampleCP(sample) * h)
                # avoid instabilities due to too small CP
                newsample = clamp(newsample, sample, regulation)
                regdelta = (heater * 0.01 * self.maxpower + heatflow -
                            self.__coolerPower(regulation))
                newregulation = max(
                    0, regulation + regdelta / self.__coolerCP(regulation) * h)
                # b) see
                # http://brettbeauregard.com/blog/2011/04/
                # improving-the-beginners-pid-introduction/
                if self.mode != Mode.openloop:
                    # fix artefacts due to too big timesteps
                    # actually i would prefer reducing looptime, but i have no
                    # good idea on when to increase it back again
                    if heatflow * lastflow != -100:
                        if (newregulation - newsample) * (regulation - sample) < 0:
                            # newregulation = (newregulation + regulation) / 2
                            # newsample = (newsample + sample) / 2
                            damper += 1
                    lastflow = heatflow

                    error = self.setpoint - newregulation
                    # use a simple filter to smooth delta a little
                    delta = (delta + regulation - newregulation) * 0.5

                    kp = self.p * 0.1             # LakeShore P = 10*k_p
                    ki = kp * abs(self.i) / 500.  # LakeShore I = 500/T_i
                    kd = kp * abs(self.d) / 2.    # LakeShore D = 2*T_d
                    _P = kp * error
                    _I += ki * error * h
                    _D = kd * delta / h

                    # avoid reset windup
                    _I = clamp(_I, 0., 100.)  # _I is in %

                    # avoid jumping heaterpower if switching back to pid mode
                    if lastmode != self.mode:
                        # adjust some values upon switching back on
                        _I = self.heater - _P - _D

                    v = _P + _I + _D
                    # in damping mode, use a weighted sum of old + new heaterpower
                    if damper > 1:
                        v = ((damper**2 - 1) * self.heater + v) / damper**2

                    # damp oscillations due to D switching signs
                    if _D * lastD < -0.2:
                        v = (v + heater) * 0.5
                    # clamp new heater power to 0..100%
                    heater = clamp(v, 0., 100.)
                    lastD = _D

                    # self.log.debug('PID: P = %.2f, I = %.2f, D = %.2f, '
                    #                'heater = %.2f', _P, _I, _D, heater)

                    # check for turn-around points to detect oscillations ->
                    # increase damper
                    x, y = last_heaters
                    if (x + 0.1 < y and y > heater + 0.1) or \
                       (x > y + 0.1 and y + 0.1 < heater):
                        damper += 1
                    last_heaters = (y, heater)

                else:
                    # self.heaterpower is set manually, not by pid
                    heater = self.heater
                    last_heaters = (0, 0)

                heater = round(heater, 1)
                sample = newsample
                regulation = newregulation
                lastmode = self.mode
                # c)
                if self.setpoint != self.target:
                    if self.ramp == 0 or self.mode == Mode.pid:
                        maxdelta = 10000
                    else:
                        maxdelta = self.ramp / 60. * h
                    try:
                        self.setpoint = round(self.setpoint + clamp(
                            self.target - self.setpoint, -maxdelta, maxdelta), 3)
                        # self.log.debug('setpoint changes to %r (target %r)',
                        #                self.setpoint, self.target)
                    except (TypeError, ValueError):
                        # self.target might be None
                        pass

                # temperature is stable when all recorded values in the window
                # differ from setpoint by less than tolerance
                currenttime = time.time()
                window.append((currenttime, sample))
                while window[0][0] < currenttime - self.window:
                    # remove old/stale entries
                    window.pop(0)
                # obtain min/max
                deviation = 0
                for _, _T in window:
                    if abs(_T - self.target) > deviation:
                        deviation = abs(_T - self.target)
                if (len(window) < 3) or deviation > self.tolerance:
                    # self.status = self.Status.BUSY, 'unstable'
                    pass
                elif self.setpoint == self.target:
                    # self.status = self.Status.IDLE, 'at target'
                    damper -= (damper - 1) * 0.1  # max value for damper is 11
                else:
                    # self.status = self.Status.BUSY, 'ramping setpoint'
                    pass
                damper -= (damper - 1) * 0.05
                self.regulationtemp = round(regulation, 3)
                self.sampletemp = round(sample, 3)
                self.heaterpower = round(heater * self.maxpower * 0.01, 3)
                self.heater = heater
                timestamp = t
                self.read_value()

    def shutdown(self):
        # should be called from server when the server is stopped
        self._stopflag = True
        if self._thread and self._thread.is_alive():
            self._thread.join()


def signal_handler(cryo, iface, log, num, frame):
    log.info('shutdown...')
    iface.shutdown()
    log.info('iface shutdown.')
    cryo.shutdown()
    log.info('cryo shutdown.')


def main(args):
    # setup logging
    log = logging.getLogger('fls')
    log.setLevel(logging.ERROR if args.quiet else logging.INFO)
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        fmt='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%H:%M:%S'
    )
    console.setFormatter(formatter)
    log.addHandler(console)
    # init simulation and interface
    lock = threading.Lock()
    cryo = Cryostat(lock, log)
    iface = Interface(args.port, lock, log, cryo)
    # graceful shutdown
    sig_handler = partial(signal_handler, cryo, iface, log)
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)
    cryo.start()
    iface.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', default=54000, type=int, help='port to listen on')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='do not print logging messages except errors')
    args = parser.parse_args(sys.argv[1:])
    main(args)
