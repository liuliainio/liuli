'''
Created on 2012-10-27

@author: qpwang
'''
import os
import zipfile
import biplist
from itemfilter import Itemfilter
from itemfilter import ItemInfo
from itemfilter import PALTFORM_IOS_PHONE, PALTFORM_IOS_PAD


class Ipafilter(Itemfilter):

    suffix = 'ipa'
    file_type = 'ipa'
    tmp_xml_file = 'tmp.xml'

    def _filter(self, file_path):
        zf = zipfile.ZipFile(file_path)
        is_break = 1
        for filename in zf.namelist():
            if filename.endswith('.app/Info.plist'):
                tmp_file = filename
                zf.extract(tmp_file)
            elif '.app/SC_Info' in filename:
                is_break = 0
        root = biplist.readPlist(tmp_file)
        command_str = 'rm -r Payload'
        os.popen(command_str)
        package_name = root.get('CFBundleIdentifier')
        if isinstance(root.get('CFBundleVersion'), str) and '.' in root.get('CFBundleVersion') and root.get('CFBundleVersion').replace('.', '').isdigit():
            version_name = root.get('CFBundleVersion')
        elif isinstance(root.get('CFBundleShortVersionString'), str) and root.get('CFBundleShortVersionString').replace('.', '').isdigit():
            version_name = root.get('CFBundleShortVersionString')
        else:
            version_name = root.get('CFBundleVersion')
        screen_support = 0
        for i in root.get('UIDeviceFamily'):
            screen_support += i
        if screen_support == 1:
            platform = PALTFORM_IOS_PHONE
        elif screen_support == 2:
            platform = PALTFORM_IOS_PAD
        elif screen_support == 3:
            platform = PALTFORM_IOS_PHONE + PALTFORM_IOS_PAD
        i = 0
        version_code = 0
        if '.' not in version_name:
            version_code = int(version_name)
        else:
            for v in version_name.split('.'):
                if i == 0:
                    v = v[:5]
                    version_code += int(v) << 50
                elif i < 4:
                    v = v[:4]
                    version_code += int(v) << 50 - i * 12
                elif i == 4:
                    v = v[:5]
                    version_code += int(v)
                if i > 4:
                    break
                i += 1
        min_sdk_version = (root.get('MinimumOSVersion').replace('.', '') + '0000')[:4]

        package_hash = self.get_package_hash(file_path)

        if package_name:
            # Get the size in bytes.
            apk_size = os.stat(file_path).st_size

            self.info = ItemInfo(package_name=package_name,
                                 version_code=int(version_code) if version_code else 0,
                                 version_name=version_name,
                                 apk_size=str(apk_size),
                                 min_sdk_version=int(min_sdk_version) if min_sdk_version else 0,
                                 screen_support=str(screen_support),
                                 is_break=is_break,
                                 file_type=self.file_type,
                                 platform=platform,
                                 package_hash=package_hash)
            return self.info
