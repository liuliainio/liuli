# encoding=utf-8
import os
import sys
import MySQLdb
import urllib2
import shutil
import urlparse

file_root = '/home/qpwang/nfs'


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
                if not apk[1] or apk[1] == 'apt':
                    request = urllib2.Request(apk[4])
                    request.add_header('Accept-encoding', 'gzip')
                    request.add_header(
                        'User-agent',
                        'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_2; en-US) AppleWebKit/533.3 (KHTML, like Gecko) Chrome/5.0.354.0 Safari/533.3')
                    r = urllib2.urlopen(request)
                    fileName = getFileName(apk[4], r)
                    if not os.path.exists('%s/vol%s%s' % (file_root, apk[3], apk[2][:6])):
                        os.makedirs('%s/vol%s%s' % (file_root, apk[3], apk[2][:6]))
                    if not fileName.endswith('.apk') and not fileName.endswith('.apt'):
                        report_list.append((apk[0], 2))
                    with open('%s/vol%s%s' % (file_root, apk[3], apk[2]), 'wb') as f:
                        shutil.copyfileobj(r, f)
                        report_list.append((apk[0], 1))
                        print '%s  finished!' % (fileName)
                    r.close()
            except Exception as e:
                print e
        report_status(report_list)


def getFileName(url, openUrl):
    if 'Content-Disposition' in openUrl.info():
        cd = dict(map(lambda x: x.strip().split('=') if '=' in x else (x.strip(), ''),
                  openUrl.info()['Content-Disposition'].split(';')))
        if 'filename' in cd:
            filename = cd['filename'].strip("\"'")
            if filename:
                return filename
    return os.path.basename(urlparse.urlsplit(openUrl.url)[2])


def report_status(list):
    for l in list:
        try:
            cursor = _db.cursor()
            if l[1] == 1:
                sql = "UPDATE final_app set is_refresh=null where id = %s"
            else:
                sql = "UPDATE final_app set is_refresh=3 where id = %s"
            cursor.execute(sql, l[0])
            _db.conn.commit()
        except MySQLdb.Error as e:
            print e
        finally:
            cursor.close()


def get_apks():
    try:
        cursor = _db.cursor()
        sql = "SELECT id,sig,file_path,vol_id,download_link from final_app where is_refresh =2 and source='91.com' limit 100"
        cursor.execute(sql)
        results = cursor.fetchall()
        return results
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()

if __name__ == "__main__":
    start_rename()
