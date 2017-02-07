#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from imap_connection import IMAP
from time import sleep
from keyboardleds import LedKit


def lights_off():
    LedKit("/dev/tty0").num_lock.reset()
    LedKit("/dev/tty0").caps_lock.reset()


def blink():
    for i in range(int(10/0.4)):
        LedKit("/dev/tty0").num_lock.toggle()
        sleep(0.2)
        LedKit("/dev/tty0").caps_lock.toggle()
        sleep(0.2)


if __name__ == "__main__":
    while True:
        conn = IMAP()
        new_mail = conn.check_for_new_mail()
        del conn
        if new_mail:
            blink()
        else:
            lights_off()
            sleep(10)
