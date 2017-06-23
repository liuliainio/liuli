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

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.db import MySQLdbWrapper

_db = MySQLdbWrapper()


def start_zip(vol_id):
    while True:
        apks = get_apks(1, vol_id[-1:])
        if not apks:
            return
        report_list = []
        try:
            command_check = 'ssh qpwang@27.17.34.243 -p' + \
                port_table[vol_id] + ' "df -h|grep /qpwang/nfs/' + vol_id[-1:] + '|tr -s \' \'|cut -d \' \' -f4"'
            command_str = 'ssh qpwang@27.17.34.243 -p' + port_table[vol_id] + ' "cd /mnt/data && tar zcf ~/move/' + \
                str(apks[0][0]) + ".tar.gz " + " ".join('%s%s' % (vol_id, apk[1]) for apk in apks) + '"'
            command_str_2 = 'ssh qpwang@27.17.34.243 -p' + \
                port_table[vol_id] + ' "cd move && md5sum ' + str(apks[0][0]) + ".tar.gz > " + str(apks[0][0]) + '.md5"'
            check_result = os.popen(command_check).read().strip()
            print check_result
            if int(check_result[:-1]) < 20:
                print 'no disk space to zip !'
                return
            else:
                os.popen(command_str)
                os.popen(command_str_2)
                report_list = apks
                report_status(report_list)
                print report_list

        except Exception as e:
            print e


def report_status(list):
    for l in list:
        try:
            cursor = _db.cursor()
            sql = "UPDATE final_app_version set is_move = %s where id = %s"
            cursor.execute(sql, (list[0][0], l[0]))
        except MySQLdb.Error as e:
            print e
        finally:
            cursor.close()
    try:
        cursor = _db.cursor()
        sql = "INSERT INTO move_apk (vol_id,file_path,status) values(%s,%s,%s)"
        cursor.execute(sql, (list[0][2], "%s.tar.gz" % list[0][0], 3))
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()


def get_apks(num, vol_id):
    try:
        cursor = _db.cursor()
        sql = "SELECT final_app_version.id, file_path, vol_id from final_app,final_app_version where final_app.id=final_app_version.id and vol_id = %s and final_app_version.is_move is null limit %d" % (
            vol_id,
            num)
        cursor.execute(sql)
        result = cursor.fetchall()
        return result
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()

if __name__ == "__main__":
    start_zip(sys.argv[1])
