# encoding=utf-8
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


def init_file(file):
    dic = {'id': file[0],
           'downloads': file[1],
           'rating': file[2],
           'version': file[3],
           'apk_size': file[4],
           'source': file[5],
           }
    return dic


def start_refresh():
    while True:
        apks = get_apks()
        if not apks:
            return
        report_list = []
        for apk in apks:
            file = init_file(apk)
            try:
                if file['source'] == 'ctmarket':
                    pass
                elif file['source'] == 'nduoa.com':
                    file['downloads'] = file['downloads'].replace(u',', '')
                    file['rating'] = get_raing(file['rating'])
                    file['apk_size'] = get_apk_size(file['apk_size'])
                elif file['source'] == 'hiapk.com':
                    file['rating'] = get_raing(file['rating'])
                    file['apk_size'] = get_apk_size(file['apk_size'])
                elif file['source'] == 'goapk.com':
                    if u'\u5927\u5c0f\uff1a' in file['downloads'].decode('utf8'):
                        file['apk_size'] = file['downloads'].decode('utf8')
                        file['downloads'] = 0
                    file['rating'] = get_raing(file['rating'])
                    file['version'] = get_version(file['version'])
                    file['apk_size'] = get_apk_size(file['apk_size'])
                elif file['source'] == 'appchina.com':
                    file['rating'] = get_raing(file['rating'])
                    file['apk_size'] = get_apk_size(file['apk_size'])
                elif file['source'] == 'mumayi.com':
                    file['rating'] = get_raing(file['rating'])
                    file['apk_size'] = get_apk_size(file['apk_size'])
                report_list.append(file)
            except Exception as e:
                print file
                print e
        report_status(report_list)


def get_raing(rating):
    if not rating:
        return 0
    rating = float(rating)
    if rating >= 10:
        rating = rating / 10
    else:
        rating = 0
    return rating


def get_version(version):
    try:
        version = version.decode('utf8')
        version = version.replace(u'\u7248\u672c\uff1a', '').strip()
    except Exception as e:
        print e
    return version


def get_apk_size(apk_size):
    if not apk_size:
        return 0
    apk_size = _adapt_colon_str(apk_size, 1)
    if ',' in apk_size:
        apk_size = apk_size.replace(',', '')
    if 'MB' in apk_size:
        apk_size = int(float(apk_size.replace('MB', '').strip()) * 1024 * 1024)
    elif 'KB' in apk_size:
        apk_size = int(float(apk_size.replace('KB', '').strip()) * 1024)
    elif 'M' in apk_size:
        apk_size = int(float(apk_size.replace('M', '').strip()) * 1024)
    elif 'K' in apk_size:
        apk_size = int(float(apk_size.replace('K', '').strip()) * 1024)
    return apk_size


def _adapt_colon_str(str, index):
    if u'\uff1a' in str:
        return str.split(u'\uff1a')[index].strip()
    elif ':' in str:
        return str.split(':')[index].strip()
    else:
        return str


def report_status(list):
    for l in list:
        try:
            cursor = _db.cursor()
            sql = "UPDATE final_app set is_refresh = 1, downloads=%s,rating=%s,version=%s,apk_size=%s where id = %s"
            cursor.execute(sql, (l['downloads'], l['rating'], l['version'], l['apk_size'], l['id']))
            cursor.connection.commit()
        except MySQLdb.Error as e:
            print e
        finally:
            cursor.close()


def get_apks():
    try:
        cursor = _db.cursor()
        sql = "SELECT id,downloads,rating,version,apk_size,source from final_app where is_refresh is null and source!='ctmarket' limit 30"
        cursor.execute(sql)
        results = cursor.fetchall()
        return results
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()


if __name__ == "__main__":
    start_refresh()
