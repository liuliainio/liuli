'''
Created on 2012-10-27

@author: qpwang
'''
import os
import zipfile
from xml.etree.ElementTree import fromstring
from itemfilter import Itemfilter
from itemfilter import MIN_SDK_VERSION_NOT_APPLIED, PALTFORM_ANDROID_PHONE, IS_BREAK_NOT_APPLIED
from itemfilter import ItemInfo


class Aptfilter(Itemfilter):

    suffix = 'apt'
    file_type = 'theme'

    def _filter(self, file_path):
        zf = zipfile.ZipFile(file_path)
        root = fromstring(zf.read('panda_theme.xml'))
        if root:
            package_name = root.get('id_flag')
            version_name = root.get('ver')
            version_code = root.get('version')
        if not package_name:
            package_name = '%s_%s' % (root.get('en_name'), file_path[-16:])

        package_hash = self.get_package_hash(file_path)

        if package_name:
            # Get the size in bytes.
            apk_size = os.stat(file_path).st_size

            self.info = ItemInfo(package_name=package_name,
                                 version_code=str(version_code) if version_code else '0',
                                 version_name=version_name,
                                 apk_size=str(apk_size),
                                 min_sdk_version=MIN_SDK_VERSION_NOT_APPLIED,
                                 screen_support=None,
                                 is_break=IS_BREAK_NOT_APPLIED,
                                 file_type=self.file_type,
                                 platform=PALTFORM_ANDROID_PHONE,
                                 package_hash=package_hash)
            return self.info
