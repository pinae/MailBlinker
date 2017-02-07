#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
import imaplib


class IMAP():
    def __init__(self):
        self.connection = imaplib.IMAP4_SSL('imap.gmail.com')
        self.connection.login('mustermann@gmail.com', 'PasswortHierEinfügen')
        self.connection.select("inbox")

    def check_for_new_mail(self):
        result, data = self.connection.uid('search', None, "(UNSEEN)")  # search and return uids instead
        try:
            newest_mail_uid = data[0].split()[0]
            return True
        except IndexError:
            return False

    def __del__(self):
        self.connection.shutdown()


if __name__ == "__main__":
    con = IMAP()
    print(con.check_for_new_mail())
