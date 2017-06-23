'''
Created on 2012-10-27

@author: qpwang
'''
import os
import re
from itemfilter import Itemfilter
from itemfilter import ItemInfo
from itemfilter import PALTFORM_ANDROID_PHONE, IS_BREAK_NOT_APPLIED
import logging

logger = logging.getLogger()

# "sudo apt-get install ia32-libs" if missing 32 bits lib
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
aapt_path = os.path.join(root_dir, 'scripts/aapt')


class Apkfilter(Itemfilter):

    suffix = 'apk'
    file_type = 'apk'

    def _filter(self, file_path):
        command = "%s dump badging %s" % (aapt_path, file_path)
        logger.info(command)

        package_name = ''
        sdk_version = ''
        lines = os.popen(command).readlines()
        for line in lines:
            values = line.split(":", 1)
            if len(values) < 2:
                continue

            k = values[0].strip().lower()
            v = values[1].strip()
            if k == "package":
                m = re.match(r"name='(.+)' versionCode='(\d*)' versionName='(.*)'", v)
                if m:
                    package_name = m.group(1)
                    version_code = m.group(2)
                    version_name = m.group(3)
                else:
                    logger.info("fail to extract info from '%s'" % v)
            elif k == "sdkversion":
                m = re.match(r"'(\d+)'", v)
                if m:
                    # This is the minimum API Level required for the application to run.
                    sdk_version = m.group(1)

        package_hash = self.get_package_hash(file_path)

        if package_name:
            # Get the size in bytes.
            apk_size = os.stat(file_path).st_size

            info = ItemInfo(package_name=package_name,
                            version_code=int(version_code) if version_code else 0,
                            version_name=version_name,
                            apk_size=str(apk_size),
                            min_sdk_version=int(sdk_version) if sdk_version else 0,
                            screen_support=None,
                            is_break=IS_BREAK_NOT_APPLIED,
                            file_type=self.file_type,
                            platform=PALTFORM_ANDROID_PHONE,
                            package_hash=package_hash)
            return info


if __name__ == "__main__":
    f = Apkfilter()
    file_path = "/home/baina/Downloads/CNDolphinJetpack.apk"
    apk_info = f._filter(file_path)
    print apk_info

