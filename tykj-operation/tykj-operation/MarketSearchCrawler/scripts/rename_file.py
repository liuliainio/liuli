# encoding=utf-8
import os
import sys
import MySQLdb

file_root = '/home/qpwang/nfs'

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.db import MySQLdbWrapper

_db = MySQLdbWrapper()


def start_rename():
    while True:
        apks = get_apks()
        if not apks:
            return
        report_list = []
        for apk in apks:
            try:
                if not apk[1] or apk[1] == 'apt':
                    os.rename(
                        '%s/vol%s%s' %
                        (file_root, apk[3], apk[2]), '%s/vol%s%s.apt' %
                        (file_root, apk[3], apk[2]))
                    report_list.append((apk[0], apk[2] + '.apt'))
                else:
                    os.rename(
                        '%s/vol%s%s' %
                        (file_root, apk[3], apk[2]), '%s/vol%s%s.apk' %
                        (file_root, apk[3], apk[2]))
                    report_list.append((apk[0], apk[2] + '.apk'))
            except Exception as e:
                print e
        report_status(report_list)


def report_status(list):
    for l in list:
        try:
            cursor = _db.cursor()
            sql = "UPDATE final_app set is_refresh=1, file_path = %s where id = %s"
            cursor.execute(sql, (l[1], l[0]))
            _db.conn.commit()
        except MySQLdb.Error as e:
            print e
        finally:
            cursor.close()


def get_apks():
    try:
        cursor = _db.cursor()
        sql = "SELECT id,sig,file_path,vol_id from final_app where is_refresh is null and source='91.com' limit 100"
        cursor.execute(sql)
        results = cursor.fetchall()
        return results
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()

if __name__ == "__main__":
    start_rename()
