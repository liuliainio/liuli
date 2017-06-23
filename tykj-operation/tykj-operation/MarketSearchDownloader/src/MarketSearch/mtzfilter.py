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


class Mtzfilter(Itemfilter):

    suffix = 'mtz'
    file_type = 'theme'

    def _filter(self, file_path):
        zf = zipfile.ZipFile(file_path)
        root = fromstring(zf.read('description.xml'))
        if root:
            package_name = file_path.split('/')[-1].split('.')[0]
            version_name = root.findtext('version')
            version_code = root.findtext('uiVersion')

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



