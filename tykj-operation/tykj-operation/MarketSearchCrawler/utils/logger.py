#-*- coding: utf-8 -*-
'''
Created on Sep 11, 2013

@author: gmliao
'''
from crawler import settings
import datetime
import sys
import threading
import traceback
import os


class Logger():
    LEVEL_DEBUG = 0
    LEVEL_INFO = 1
    LEVEL_WARN = 2
    LEVEL_ERROR = 3
    LEVEL_NONE = 4

    def __init__(self, log_file=None):
        self.level = self.LEVEL_DEBUG
        if not log_file:
            self.log_file = sys.stdout
        else:
            if not os.path.exists(os.path.dirname(os.path.abspath(log_file))):
                os.makedirs(os.path.dirname(os.path.abspath(log_file)))
            self.log_file = file(log_file, 'a')

    def _write_log(self, msg):
        self.log_file.write(msg)
        self.log_file.write('\n')
        self.log_file.flush()

    def now(self):
        return datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')

    def trace(self):
        trace = traceback.extract_stack()
        trace = trace[len(trace) - 3]
        trace = u'[%s %s: %s]' % (trace[0], trace[2], trace[1])
        return trace

    def i(self, msg):
        if self.level > self.LEVEL_INFO:
            return
        msg = self.normal_msg(msg)
        self._write_log(u'[INFO] %s %s %s: %s' % (threading.current_thread().name,
                                                  self.trace(), self.now(), msg.decode('utf-8')))

    def normal_msg(self, msg):
        if msg is None:
            msg = ''
        elif type(msg) in [unicode, str]:
            msg = msg.encode('utf-8')
        else:
            msg = str(msg)
        return msg

    def w(self, msg):
        if self.level > self.LEVEL_WARN:
            return
        msg = self.normal_msg(msg)
        self._write_log(u'[WARN] %s %s %s: %s' % (threading.current_thread().name,
                                                  self.trace(), self.now(), msg.decode('utf-8')))

    def d(self, msg):
        if self.level > self.LEVEL_DEBUG:
            return
        if settings.DEBUG:
            msg = self.normal_msg(msg)
            self._write_log(u'[DEBUG] %s %s %s: %s' % (threading.current_thread().name,
                                                       self.trace(), self.now(), msg.decode('utf-8')))

    def e(self, msg):
        if self.level > self.LEVEL_ERROR:
            return
        msg = self.normal_msg(msg)
        self._write_log(u'[ERROR] %s %s %s: %s' % (threading.current_thread().name,
                                                   self.trace(), self.now(), msg.decode('utf-8')))
        self._write_log(traceback.format_exc())

logger = Logger()
