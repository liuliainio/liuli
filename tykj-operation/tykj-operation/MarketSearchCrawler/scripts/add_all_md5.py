# coding=utf-8
import os
from hashlib import md5
import MySQLdb
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.db import MySQLdbWrapper

_db = MySQLdbWrapper()


def check_app():
    i = 0
    while True:
        apps = get_apps()
        if not apps:
            return
        report_list = []
        for app in apps:
            try:
                i += 1
                vol_id = app[1]
                download_link = app[2]
                file_type = app[3]
                file_name = md5(download_link).hexdigest().upper()
                if int(vol_id) in [2, 3, 4, 5, 11]:
                    file_root = '/mnt/ctappstore1/'
                elif int(vol_id) in [1, 6, 7, 8, 10]:
                    file_root = '/mnt/ctappstore2/'
                elif int(vol_id) in [9, 13, 14]:
                    file_root = '/mnt/ctappstore3/'
                elif int(vol_id) in [107, 155, 156, 157, 158, 159, 161, 162, 163, 164]:
                    file_root = '/mnt/ctappstore100/'
                path = '%svol%s/%s/%s/%s.%s' % (file_root, vol_id, file_name[:2], file_name[2:4], file_name, file_type)
                command = 'md5sum %s' % path
                package_hash = os.popen(command).read()
                if not package_hash:
                    package_hash = '-1'
                else:
                    package_hash = package_hash.split()[0]
                report_list.append((app[0], package_hash))
                print i, path, package_hash
            except Exception as e:
                print app
                print e
        report_status(report_list)


def report_status(list):
    for l in list:
        try:
            cursor = _db.cursor()
            sql = "UPDATE final_app set package_hash=%s where id = %s"
            cursor.execute(sql, (l[1], l[0]))
            cursor.connection.commit()
        except MySQLdb.Error as e:
            print e
        finally:
            cursor.close()


def get_apps():
    try:
        cursor = _db.cursor()
        sql = "SELECT id,vol_id,download_link,file_type from final_app where (file_type='apk' or file_type='ipa') and package_hash is null order by id desc limit 100"
        cursor.execute(sql)
        results = cursor.fetchall()
        sql = "update final_app set package_hash=1 where (file_type='apk' or file_type='ipa') and package_hash is null order by id desc limit 100"
        cursor.execute(sql)
        _db.conn.commit()
        return results
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()


if __name__ == "__main__":
    check_app()
