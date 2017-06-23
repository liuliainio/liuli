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

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.db import MySQLdbWrapper

_db = MySQLdbWrapper()


def start_move(vol_id):
    while True:
        apk = get_apks(vol_id[-1:])
        if not apk:
            return
        report_list = []
        try:
            command_str = 'scp -P' + port_table[vol_id] + \
                ' qpwang@27.17.34.243:/home/qpwang/move/%s %s' % (apk[0], fs_root)
            command_str_2 = 'scp -P' + port_table[vol_id] + \
                ' qpwang@27.17.34.243:/home/qpwang/move/%s.md5 %s' % (apk[0].split('.')[0], fs_root)
            command_str_3 = 'cd %s && md5sum -c %s.md5' % (fs_root, apk[0].split('.')[0])
            command_str_4 = 'ssh qpwang@27.17.34.243 -p' + \
                port_table[vol_id] + ' "cd %s && rm %s %s.md5"' % (fs_root, apk[0], apk[0].split('.')[0])
            command_str_5 = 'cd %s && rm %s.md5' % (fs_root, apk[0].split('.')[0])
            print command_str_4
            os.popen(command_str)
            os.popen(command_str_2)
            print 'download %s finished!' % apk[0]
            result = os.popen(command_str_3).read().strip().split(':')[1].decode('utf8').strip()
            if result == u'确定' or result == 'ok':
                print 'check %s success' % apk[0]
                os.popen(command_str_4)
                report_status(apk[1])
            else:
                print 'check %s false' % apk[0]
            os.popen(command_str_5)
        except Exception as e:
            print e


def report_status(id):
    try:
        cursor = _db.cursor()
        sql = "UPDATE move_apk set status = %s where id = %s"
        cursor.execute(sql, (1, id))
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()


def get_apks(vol_id):
    try:
        cursor = _db.cursor()
        sql = "SELECT file_path,id from move_apk where status=3 and vol_id=%s limit 1" % vol_id
        cursor.execute(sql)
        result = cursor.fetchone()
        return result
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()

if __name__ == "__main__":
    start_move(sys.argv[1])
