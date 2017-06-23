# encoding=utf-8
import os
import sys
import simplejson
import MySQLdb
import zipfile
from xml.etree.ElementTree import fromstring
from hashlib import md5

FS_ROOT = '/home/qpwang/nfs'

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.db import MySQLdbWrapper

_db = MySQLdbWrapper()


def get_str_md5(str=None):
    return md5(str).hexdigest().upper()


def get_path(vol_id, key_url, suffix):
    vol_id = 'vol%s' % vol_id
    md5 = get_str_md5(key_url)
    dir1 = md5[:2]
    dir2 = md5[2:4]
    name = '%s.%s' % (md5, suffix)
    if not os.path.exists(os.path.join(FS_ROOT, vol_id, dir1, dir2)):
        os.makedirs(os.path.join(FS_ROOT, vol_id, dir1, dir2))
    return os.path.join(FS_ROOT, vol_id, dir1, dir2, name)


def start_refresh():
    while True:
        apks = get_apks()
        if not apks:
            print 'finished'
            return
        report_list = []
        for apk in apks:
            try:
                file_path = get_path('10', apk[1], 'mtz')
                zf = zipfile.ZipFile(file_path)
                root = fromstring(zf.read('description.xml'))
                if root:
                    versionName = root.findtext('version')
                    versionCode = root.findtext('uiVersion')
                report_list.append((apk[0], versionName, versionCode))
            except Exception as e:
                print file
                print e
        report_status(report_list)


def report_status(list):
    for l in list:
        try:
            cursor = _db.cursor()
            sql = "UPDATE unique_apk set version=%s, version_code=%s where id = %s"
            cursor.execute(sql, (l[1], l[2], l[0]))
            cursor.connection.commit()
        except MySQLdb.Error as e:
            print e
        finally:
            cursor.close()


def get_apks():
    try:
        cursor = _db.cursor()
        sql = "SELECT id,download_link from unique_apk where version is null and source='zhuti.xiaomi.com' limit 30"
        cursor.execute(sql)
        results = cursor.fetchall()
        return results
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()


if __name__ == "__main__":
    start_refresh()
