# encoding=utf-8
import os
import sys
import simplejson
import MySQLdb

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.db import MySQLdbWrapper

_db = MySQLdbWrapper()


def start_update():
    while True:
        ipas = get_ipas()
        if not ipas:
            return
        report_list = []
        version_code = 0
        i = 0
        for ipa in ipas:
            for v in ipa[1].split('.'):
                version_code += int(v) << (48 - i * 16)
                i += 1
                if i > 4:
                    break
        report_list.append((ipa[0], version_code))
        report_status(report_list)


def report_status(list):
    for l in list:
        try:
            cursor = _db.cursor()
            sql = "UPDATE unique_apk set version_code = %s, tag=1 where id = %s"
            cursor.execute(sql, (l[1], l[0]))
            _db.conn.commit()
        except MySQLdb.Error as e:
            print e
        finally:
            cursor.close()


def get_ipas():
    try:
        cursor = _db.cursor()
        sql = "SELECT id,version from unique_apk where tag is null and source='ipa.91.com' limit 100"
        cursor.execute(sql)
        results = cursor.fetchall()
        return results
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()


if __name__ == "__main__":
    start_update()
