#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
import keyboardleds
import time

if __name__ == "__main__":
    while True:
        keyboardleds.LedKit("/dev/tty0").num_lock.toggle()
        time.sleep(0.2)
        keyboardleds.LedKit("/dev/tty0").caps_lock.toggle()
        time.sleep(0.2)
