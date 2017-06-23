# encoding=utf-8

import MySQLdb
import simplejson
import sys
import os
from datetime import datetime
from time import mktime


def init_db(host='localhost', user='market', password='P@55word', name='market'):
    global conn
    conn = MySQLdb.connect(host, user, password, name)
    conn.set_character_set('utf8')


def get_epoch_datetime(value=None):
    if not value:
        value = datetime.utcnow()
    try:
        return int(mktime(value.timetuple()))
    except AttributeError:
        return None


def parse(path):
    files = os.listdir(path)
    print files
    sum = len(files)
    count = 0
    id_pool = []
    for file in files:
        count += 1
        try:
            cursor = conn.cursor()
            file_path = path + file
            tmp = []
            file = open(file_path, 'r')
            for r in file.readlines():
                res = r.split('|')
                if len(res) < 10:
                    continue
                id = res[0]
                name = res[1]
                link = res[5]
                img_link = res[6]
                price = res[13]
                tmp.append((name, img_link, 'walmart.com', link, price, get_epoch_datetime()))
            cursor.executemany("""INSERT  IGNORE INTO  walmart
                    (name, image_link, source, source_link,
                     salePrice, updated) VALUES (%s, %s, %s,
                     %s, %s, %s)""", tmp)
            print '%s finished!  %s/%s' % (file_path, count, sum)
        except MySQLdb.Error as e:
            print e
        finally:
            conn.commit()  # commit all together at once
            cursor.close()


if __name__ == "__main__":
    init_db()
    parse(sys.argv[1])
