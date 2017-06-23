'''
Created on 2012-10-23

@author: qpwang
'''
from datetime import datetime
from time import mktime
from hashlib import md5


def get_str_md5(str=None):
    return md5(str).hexdigest().upper()


def get_epoch_datetime(value=None):
    if not value:
        value = datetime.utcnow()
    try:
        return int(mktime(value.timetuple()))
    except AttributeError:
        return None
