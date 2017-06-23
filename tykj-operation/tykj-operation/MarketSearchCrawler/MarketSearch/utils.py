'''
Created on Jun 2, 2011

@author: yan
'''
from datetime import datetime
from hashlib import md5
from scrapy import log
from time import mktime
import os


def get_epoch_datetime(value=None):
    if not value:
        value = datetime.utcnow()
    try:
        return int(mktime(value.timetuple()))
    except AttributeError:
        return None


def get_str_md5(str=None):
    return md5(str).hexdigest().upper()


def strip_space(text):
    return text.strip() if text else ''


def ensure_dir(dir):
    '''
    Ensure a certain directory exits.
    '''
    if not os.path.exists(dir):
        os.makedirs(dir)


def log_error(msg):
    import traceback
    traceback.print_exc()
    log.msg(msg, level=log.ERROR)


def log_warning(msg):
    log.msg(msg, level=log.WARNING)


def log_info(msg):
    log.msg(msg, level=log.INFO)
