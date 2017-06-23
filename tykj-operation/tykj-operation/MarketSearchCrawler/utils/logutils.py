#-*- coding: utf-8 -*-
'''
Created on Dec 2, 2013

@author: gmliao
'''

from watchdog.events import LoggingEventHandler
from watchdog.observers import Observer
import logging
import os
import threading


_inited_logger = {}
_def_formatter = logging.Formatter(
    '[%(levelname)s] %(asctime)s %(process)d %(thread)d [%(module)s.%(funcName)s line:%(lineno)d]: %(message)s')

logfileobserver = Observer()
logfileobserver.start()
_watched_dirs = []
_lock = threading.Lock()


def config_logger(name=None, filename=None, formatter=None, level=logging.INFO, console=None, reconfig=False):
    with _lock:
        return _config_logger(name, filename, formatter, level, console, reconfig)


def _config_logger(name=None, filename=None, formatter=None, level=logging.INFO, console=None, reconfig=False):
    if name is None:
        name = 'root'
    if name in _inited_logger and not reconfig:
        return logging.getLogger(name)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    filename = filename or '%s.log' % __name__
    formatter = formatter or _def_formatter

    if reconfig:
        for h in logger.handlers[:]:
            logger.removeHandler(h)

    dirname = os.path.dirname(os.path.abspath(filename))
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    if dirname not in _watched_dirs:
        logfileobserver.schedule(ReconfigLoggerEventHandler(), dirname, False)
        _watched_dirs.append(dirname)

    fh = logging.FileHandler(filename)
    fh.setFormatter(formatter)
    fh.setLevel(level)
    logger.addHandler(fh)

    if console is None:
        console = level <= logging.DEBUG
    if console:
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        ch.setLevel(level)
        logger.addHandler(ch)
    _inited_logger[name] = (logger, (name, filename, formatter, level, console))
    return logger


class ReconfigLoggerEventHandler(LoggingEventHandler):

    def _reconfig_logger(self, event):
        for _, args in _inited_logger.values():
            if os.path.abspath(args[1]) == os.path.abspath(event.src_path):
                args = list(args)
                args.append(True)
                config_logger(*args)

    def on_deleted(self, event):
        LoggingEventHandler.on_deleted(self, event)
        self._reconfig_logger(event)

    def on_moved(self, event):
        LoggingEventHandler.on_moved(self, event)
        self._reconfig_logger(event)
