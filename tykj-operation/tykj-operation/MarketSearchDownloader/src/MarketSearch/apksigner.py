'''
Created on 2012-11-2

@author: qpwang
'''
import os
import sys
import time
import service
from file import get_path
from gen.ttypes import ApkFileStatus


class Apksigner(object):

    def start_singer(self):

        while True:
            files = service.get_uniq_apk_files('', 0)
            status_list = []
            if not files:
                print 'singer finished!'
                return
            for souce_link, key_url, source, vol_id in files:
                try:
                    sig = self.sign(key_url, vol_id)
                    if sig:
                        status_list.append(ApkFileStatus(souce_link, key_url, source, 1, vol_id, sig))
                    else:
                        status_list.append(ApkFileStatus(souce_link, key_url, source, 2, vol_id))
                except Exception as e:
                    status_list.append(ApkFileStatus(souce_link, key_url, source, 2, vol_id))
                    print e

            service.report_uniq_apk_file_status(status_list)
            time.sleep(1)

    def sign(self, key_url, vol_id):

        file_path = get_path(vol_id, key_url, 'apk')
        command_str = 'java -jar ../../scripts/getSign.jar %s' % file_path

        return os.popen(command_str).read().strip()


if __name__ == "__main__":
    s = Apksigner()
    s.start_singer()
