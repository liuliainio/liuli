# coding=utf-8
import os
import sys
import simplejson
import MySQLdb


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


def start_check():
    while True:
        apks = get_apks()
        if not apks:
            return
        report_list = []
        for apk in apks:

            try:
                url = ''
                if apk[3] == 'ctmarket':
                    url = 'http://221.237.156.84:7788/downloads/%s' % apk[1]
                else:
                    url = apk[0]
                command_str = 'curl -k -d \'{"authkey":"9ORmsDOAJ3zcD21w", "url":"%s"}\' https://api.scan.qq.com/browser/scan' % url
                result = os.popen(command_str).read().strip()
                status = simplejson.loads(result)
                if status.get('safetype') == 'safe':
                    print status.get('safetype')
                report_list.append((apk[2], status.get('safetype')))
            except Exception as e:
                print e
        report_status(report_list)


def report_status(list):
    for l in list:
        try:
            cursor = _db.cursor()
            sql = "UPDATE final_app_version set security_status = %s where id = %s"
            cursor.execute(sql, (l[1], l[0]))
        except MySQLdb.Error as e:
            print e
        finally:
            cursor.close()


def get_apks():
    try:
        cursor = _db.cursor()
        sql = "SELECT download_link,file_path,final_app_version.id,source from final_app,final_app_version where final_app.id = final_app_version.id and final_app_version.security_status is null limit 30"
        cursor.execute(sql)
        results = cursor.fetchall()
        return results
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()


if __name__ == "__main__":
    start_check()
