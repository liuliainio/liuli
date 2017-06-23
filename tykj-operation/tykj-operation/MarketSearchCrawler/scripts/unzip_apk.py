# coding=utf-8
import os
import sys
import MySQLdb

port_table = {'vol2': '70',
              'vol3': '71',
              'vol4': '66',
              'vol5': '67',
              'vol6': '68',
              }

fs_root = '~/move'
nfs_root = '~/move'

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.db import MySQLdbWrapper

_db = MySQLdbWrapper()


def start_unzip(vol_id):
    while True:
        apk = get_apks(vol_id[-1:])
        if not apk:
            return
        report_list = []
        try:
            command_str = 'cd %s && tar zxf %s/%s' % (nfs_root, fs_root, apk[0])
            command_str_2 = 'rm %s/%s' % (fs_root, apk[0])
            print command_str
            os.popen(command_str)
            print 'unzip %s finished!' % apk[0]
            report_status(apk[1])
            os.popen(command_str_2)
        except Exception as e:
            print e


def report_status(id):
    try:
        cursor = _db.cursor()
        sql = "UPDATE move_apk set status = %s where id = %s"
        cursor.execute(sql, (2, id))
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()


def get_apks(vol_id):
    try:
        cursor = _db.cursor()
        sql = "SELECT file_path,id from move_apk where status=1 and vol_id=%s limit 1" % vol_id
        cursor.execute(sql)
        result = cursor.fetchone()
        return result
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()

if __name__ == "__main__":
    start_unzip(sys.argv[1])
