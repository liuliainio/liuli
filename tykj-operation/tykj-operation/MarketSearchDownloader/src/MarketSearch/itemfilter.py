'''
Created on 2012-10-27

@author: qpwang
'''
import os
import errno
from collections import namedtuple
from file import get_path


ItemInfo = namedtuple(
    'ItemInfo',
    ['package_name',
     'version_code',
     'min_sdk_version',
     'version_name',
     'apk_size',
     'screen_support',
     'is_break',
     'file_type',
     'platform',
     'package_hash'])
MIN_SDK_VERSION_NOT_APPLIED = -1
IS_BREAK_NOT_APPLIED = -1
PALTFORM_ANDROID_PHONE = 1
PALTFORM_ANDROID_PAD = 2
PALTFORM_IOS_PHONE = 4
PALTFORM_IOS_PAD = 8


class Itemfilter(object):

    file_path = ''
    suffix = ''

    def filter(self, key_url, vol_id):
        self.file_path = get_path(vol_id, key_url, self.suffix)
        return self._filter(self.file_path)

    def _filter(self, file_path):
        pass

    def silent_remove(self, filename):
        try:
            os.remove(filename)
            print '%s deleted!' % filename
            return True
        except OSError as e:  # this would be "except OSError as e:" in python 3.x
            if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
                print e  # re-raise exception if a different error occured

    def get_package_hash(self, file_path):
        command = 'md5sum %s' % file_path
        package_hash = os.popen(command).read().split()[0]
        return package_hash
