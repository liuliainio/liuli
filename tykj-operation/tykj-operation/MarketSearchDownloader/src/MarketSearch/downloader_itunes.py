# encoding=utf-8
'''
Created on 2012-10-23

@author: qpwang
'''
import urllib2
import shutil
import urlparse
import os
import sys
import service
from gen.ttypes import ApkStatus, ApkFileStatus
from file import get_path, get_vol
from apkfilter import Apkfilter
from apksigner import Apksigner
from aptfilter import Aptfilter
from mtzfilter import Mtzfilter
from ipafilter import Ipafilter
from db import is_apk_exist

ipafilter = Ipafilter()


class ApkDownloader(object):

    name = ''
    file_path = ''

    def start(self, name, isUpdate=False):
        self.name = name
        while True:
            if isUpdate:
                apks = service.get_update_apk_links(self.name, 250)
            else:
                apks = service.get_apk_links(self.name, 250)
            if not apks:
                print 'no apks!'
                return
            for source_link, key_url, size in apks:
                r = self.download(source_link, key_url, size)
                if not r:
                    print 'not disk!!!!!!!!!!!!!!!!!!!!!!!!!!!'
                    return 0

    def download(self, source_link, key_url, size, fileName=None):
        if self.name in ['91.com']:
            vol_id = '10'
            suffix = 'apt'
        elif self.name in ['zhuti.xiaomi.com', 'lock.xiaomi.com', 'icon.xiaomi.com', 'font.xiaomi.com']:
            vol_id = '10'
            suffix = 'mtz'
        elif self.name in ['ipa.91.com', 'ipa.kuaiyong.com']:
            vol_id = get_vol(self.name)
            suffix = 'ipa'
        else:
            vol_id = get_vol(self.name)
            suffix = 'apk'
        if not vol_id:
            return None
        self.file_path = get_path(vol_id, key_url, suffix)
        try:
            request = urllib2.Request(key_url)
            request.add_header('Accept-encoding', 'gzip')
            request.add_header(
                'User-agent',
                'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_2; en-US) AppleWebKit/533.3 (KHTML, like Gecko) Chrome/5.0.354.0 Safari/533.3')
            if self.name == 'hiapk.com':
                request.add_header('Referer', 'http://apk.hiapk.com')
            r = urllib2.urlopen(request)
            fileName = fileName or self.getFileName(key_url, r)
            if not (fileName.endswith('.apk') or fileName.endswith('.apt') or fileName.endswith('.mtz') or fileName.endswith('.ipa')):
                service.report_apk_status([ApkStatus(source_link, key_url, self.name, 2, vol_id, fileName)])
                return
            with open(self.file_path, 'wb') as f:
                print '%s  star! size:%s' % (fileName, size)
                shutil.copyfileobj(r, f)
                service.report_apk_status([ApkStatus(source_link, key_url, self.name, 1, vol_id, fileName)])
                print '%s  finished! size:%s' % (fileName, size)
            r.close()
            self.filter_item(key_url, vol_id, source_link, fileName)

        except Exception as e:
            print e
        finally:
            return True

    def getFileName(self, url, openUrl):
        if 'Content-Disposition' in openUrl.info():
            cd = dict(
                map(lambda x: x.strip().split('=') if '=' in x else (x.strip(),
                                                                     ''),
                    openUrl.info()['Content-Disposition'].split(';')))
            if 'filename' in cd:
                filename = cd['filename'].strip("\"'")
                if filename:
                    return filename
        return os.path.basename(urlparse.urlsplit(openUrl.url)[2])

    def filter_item(self, key_url, vol_id, source_link, fileName):
        if fileName.endswith('.apk'):
            itemfilter = apkfilter
            sig = apksigner.sign(key_url, vol_id)
        elif fileName.endswith('.ipa'):
            itemfilter = ipafilter
            sig = 'ipa'
        elif fileName.endswith('.mtz'):
            itemfilter = mtzfilter
            sig = 'mtz'
        elif fileName.endswith('.apt'):
            itemfilter = aptfilter
            sig = 'apt'
        item = itemfilter.filter(key_url, vol_id)
        if is_apk_exist(item.package_name, item.version_code, item.file_type, item.is_break, key_url) or not item or (item.file_type == 'ipa' and item.is_break == 0):
            result = apkfilter.silent_remove(self.file_path)
            if result:
                print 'vol_id:%s, download_url:%s deleted!' % (vol_id, key_url)
                service.remove_apk(
                    [ApkFileStatus(source_link,
                                   key_url,
                                   self.name,
                                   1,
                                   vol_id,
                                   item.package_name,
                                   item.version_code)])
            else:
                service.remove_apk(
                    [ApkFileStatus(source_link,
                                   key_url,
                                   self.name,
                                   2,
                                   vol_id,
                                   item.package_name,
                                   item.version_code)])
        else:
            service.insert_apk(
                [ApkFileStatus(source_link,
                               key_url,
                               self.name,
                               1,
                               vol_id,
                               item.package_name,
                               item.version_code,
                               sig,
                               item.version_name,
                               item.apk_size,
                               item.min_sdk_version,
                               item.screen_support,
                               item.is_break,
                               item.file_type,
                               item.platform,
                               item.package_hash)])

if __name__ == "__main__":
    d = ApkDownloader()
    if len(sys.argv) > 2:
        d.start(sys.argv[1], True)
    elif len(sys.argv) == 2:
        d.start(sys.argv[1])
    else:
        d.start('goapk.com', True)
