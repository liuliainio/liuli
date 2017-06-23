# encoding=utf-8
import os
import sys
import simplejson
import MySQLdb
from BeautifulSoup import BeautifulSoup


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


def start_refresh():
    while True:
        apks = get_apks()
        if not apks:
            return
        report_list = []
        for apk in apks:
            try:
                if not apk[1]:
                    desc = ''
                else:
                    soup = BeautifulSoup(apk[1])
                    desc = soup.getText('\n')
                report_list.append((apk[0], desc))
            except Exception as e:
                print file
                print e
        report_status(report_list)


def _adapt_colon_str(str, index):
    if u'\uff1a' in str:
        return str.split(u'\uff1a')[index].strip()
    elif ':' in str:
        return str.split(':')[index].strip()
    else:
        return ''


def report_status(list):
    for l in list:
        try:
            cursor = _db.cursor()
            sql = "UPDATE final_app set is_refresh=1, description = %s where id = %s"
            cursor.execute(sql, (l[1], l[0]))
            cursor.connection.commit()
        except MySQLdb.Error as e:
            print e
        finally:
            cursor.close()


def get_apks():
    try:
        cursor = _db.cursor()
        sql = "SELECT id,description from final_app where is_refresh is null and source !='ctmarket' limit 30"
        cursor.execute(sql)
        results = cursor.fetchall()
        return results
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()


if __name__ == "__main__":
    start_refresh()
