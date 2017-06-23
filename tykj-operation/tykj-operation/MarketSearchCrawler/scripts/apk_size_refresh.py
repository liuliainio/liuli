# encoding=utf-8
import os
import sys
import MySQLdb
import urllib2
import shutil
import urlparse

file_root = '/home/qpwang/img/'


class MySQLdbWrapper:

    conn = None

    def connect(self):
        self.conn = MySQLdb.connect('localhost', 'root', 'P@55word', 'market')
        self.conn.set_character_set('utf8')

    def cursor(self):
        try:
            if not self.conn:
                self.connect()
            return self.conn.cursor()
        except MySQLdb.OperationalError:
            self.connect()
            return self.conn.cursor()

_db = MySQLdbWrapper()


def start_rename():
    while True:
        apks = get_apks()
        if not apks:
            return
        report_list = []
        for apk in apks:
            try:
                command_str1 = 'ls -l %s%s|cut -d " " -f5' % (file_root, apk[1])
                command_str2 = 'identify %s%s|cut -d " " -f3' % (file_root, apk[1])
                apk_size = os.popen(command_str1).read().strip()
                screen = os.popen(command_str2).read().strip()
                report_list.append((apk[0], apk_size, screen))
            except Exception as e:
                print e
        report_status(report_list)


def report_status(list):
    for l in list:
        try:
            cursor = _db.cursor()
            sql = "UPDATE img set screen_support=%s,apk_size=%s where id = %s"
            cursor.execute(sql, (l[2], l[1], l[0]))
            _db.conn.commit()
        except MySQLdb.Error as e:
            print e
        finally:
            cursor.close()


def get_apks():
    try:
        cursor = _db.cursor()
        sql = "SELECT id,icon_path from img where apk_size is null limit 100"
        cursor.execute(sql)
        results = cursor.fetchall()
        return results
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()

if __name__ == "__main__":
    start_rename()
