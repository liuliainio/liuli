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


def _get_date(datetime_str):
        if not datetime_str:
            return None
        month = datetime_str.split('-')[1].strip()
        day = datetime_str.split('-')[2].split('T')[0].strip()
        year = datetime_str.split('-')[0].strip()
        hour = datetime_str.split('T')[1].split(':')[0].strip()
        min = datetime_str.split('T')[1].split(':')[1].strip()
        sec = datetime_str.split('T')[1].split(':')[2].strip()
        date = datetime.strptime(year + month + day + hour + min + sec, "%Y%m%d%H%M%S")
        return get_epoch_datetime(date)


def get_epoch_datetime(value=None):
    if not value:
        value = datetime.utcnow()
    try:
        return int(mktime(value.timetuple()))
    except AttributeError:
        return None


def parse(path):
    files = os.listdir(path)
    sum = len(files)
    count = 0
    for file in files:
        count += 1
        try:
            cursor = conn.cursor()
            tmp = []
            file_path = path + file
            file = open(file_path, 'r')
            data = file.read()
            res = simplejson.loads(data)
            for r in res:
                if not r.get('name'):
                    continue
                tmp.append((r.get('name'), r.get('thumbnailImage'), 'bestbuy.com',
                            'http://www.bestbuy.com/site/%s/%s.p?id=%s&skuId=%s' %
                            (r.get('name'), r.get('sku'), r.get('productId'), r.get('sku')),
                            r.get('customerReviewAverage'), r.get('customerReviewCount'),
                            r.get('sku'), r.get('productId'), r.get('quantityLimit'),
                            r.get('salePrice'), _get_date(r.get('itemUpdateDate')),
                            r.get('manufacturer'), r.get('itemCondition'), r.get('onSale')))
            cursor.executemany("""INSERT INTO  bestbuy
                (name, image_link, source, source_link,
                 customerReviewAverage, customerReviewCount,
                 sku, productId, quantityLimit,
                 salePrice, itemUpdateDate, manufacturer,
                 itemCondition, onSale) VALUES (%s, %s, %s,
                 %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", tmp)
            print '%s finished!  %s/%s' % (file_path, count, sum)
        except MySQLdb.Error as e:
            print e
        finally:
            conn.commit()  # commit all together at once
            cursor.close()


if __name__ == "__main__":
    init_db()
    parse(sys.argv[1])
