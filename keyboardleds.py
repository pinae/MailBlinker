# encoding=UTF-8

# Copyright © 2009-2015 Jakub Wilk <jwilk@jwilk.net>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


'''
>>> lk = LedKit('/dev/tty')
>>> lk.caps_lock.set()
>>> lk.caps_lock.reset()
>>> lk.caps_lock.toggle()
'''

import sys

_p_linux = sys.platform.startswith('linux')

if not _p_linux:
    raise NotImplementedError(
        'the {sys.platform!r} platform is not supported'.format(sys=sys)
    )

if _p_linux:

    import time
    import fcntl
    import os
    import stat
    import struct

    _KDGETLED = 0x4B31
    _KDSETLED = 0x4B32

    _tty_leds = dict(
        scroll_lock=0x01,
        num_lock=0x02,
        caps_lock=0x04,
    )

    _EV_LED = 0x11

    _input_leds = dict(
        num_lock=0x00,
        caps_lock=0x01,
        scroll_lock=0x02,
        compose=0x03,
        kana=0x04,
        sleep=0x05,
        suspend=0x06,
        mute=0x07,
        misc=0x08,
        mail=0x09,
        charging=0x0a,
    )

    _EVENT_DEV_MIN = 0x0D40
    _EVENT_DEV_MAX = _EVENT_DEV_MIN + 0x20 - 1

_MAGIC = []


class LedKit(object):

    if _p_linux:

        def __init__(self, device_path):
            self._filename = device_path
            self._fd = os.open(device_path, os.O_WRONLY)
            info = os.fstat(self._fd)
            self._input_subsystem = (
                stat.S_ISCHR(info.st_mode) and
                _EVENT_DEV_MIN <= info.st_rdev <= _EVENT_DEV_MAX
            )
            self._leds = {}
            if self._input_subsystem:
                self.get = self._get_standalone
                self.set = self._set_standalone
                for name, n in _input_leds.items():
                    InputEventLed(self, name, n, magic=_MAGIC)
            else:
                for name, n in _tty_leds.items():
                    Led(self, name, n, magic=_MAGIC)

        def __del__(self):
            try:
                os.close(self._fd)
            except AttributeError:
                pass

        def _set(self, n):
            fcntl.ioctl(self._fd, _KDSETLED, n)

        def _get(self):
            if self._input_subsystem:
                raise NotImplementedError
            bytes = struct.pack('I', 0)
            bytes = fcntl.ioctl(self._fd, _KDGETLED, bytes)
            [result] = struct.unpack('I', bytes)
            return result

    def set(self, lights):
        n = 0
        for light in lights:
            n |= light._n
        self._set(n)

    def _set_standalone(self, lights):
        lights = set(lights)
        offs = set(self._leds.values()) - lights
        for led in offs:
            led.reset()
        for led in lights:
            led.set()

    def get(self):
        n = self._get()
        result = []
        i = 1
        while i <= n:
            if n & i != 0:
                try:
                    result.append(self._leds[i])
                except KeyError:
                    pass
            i *= 2
        return result

    def _get_standalone(self):
        return [led for led in self._leds.values() if led.get()]

    def __repr__(self):
        return '{mod}.{cls}({file!r})'.format(
            mod=type(self).__module__,
            cls=type(self).__name__,
            file=self._filename,
        )


class Led(object):

    standalone = False

    def __init__(self, control, name, n, magic=None):
        if magic is not _MAGIC:
            raise RuntimeError('You are not supposed to create these objects')
        self._control = control
        self._name = name
        self._n = n
        control._leds[n] = self
        setattr(control, name, self)

    def set(self):
        c = self._control
        c._set(c._get() | self._n)

    def toggle(self):
        c = self._control
        c._set(c._get() ^ self._n)

    def reset(self):
        c = self._control
        c._set(c._get() & ~self._n)

    def get(self):
        c = self._control
        return c._get() & self._n != 0

    def __repr__(self):
        return '{ctrl}.{name}'.format(ctrl=self._control, name=self._name)

if _p_linux:

    class InputEventLed(Led):

        standalone = True

        def _set(self, value):
            now = time.time()
            sec = int(now)
            usec = int((now - sec) * 1.0E6)
            data = struct.pack('@llHHI', sec, usec, _EV_LED, self._n, value)
            os.write(self._control._fd, data)

        def set(self):
            self._set(1)

        def toggle(self):
            raise NotImplementedError

        def reset(self):
            self._set(0)

        def get(self):
            raise NotImplementedError

# vim:ts=4 sts=4 sw=4 et
