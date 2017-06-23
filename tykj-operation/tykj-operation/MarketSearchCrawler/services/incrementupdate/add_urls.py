#-*- coding: utf-8 -*-
'''
Created on Feb 19, 2014

@author: gmliao
'''
import datetime
from services.db import MySQLdbWrapper
from _mysql_exceptions import MySQLError
import pika
from crawler import settings
import traceback
from utils import logger
import sys
import os
import time

_db = MySQLdbWrapper()
logger = logger.Logger('/var/app/log/MarketSearchCrawler/incrementupdate-add_urls.log')


def get_urls_from_finalapp(last_minutes):
    now = datetime.datetime.now()
    start = now - datetime.timedelta(minutes=last_minutes)
    sql = 'select avail_download_links from final_app where updated_at >= %s'
    urls = set()
    try:
        c = _db.cursor()
        c.execute(sql, (start, ))
        result = c.fetchall()
        for r in result:
            for u in r[0].split(' '):
                urls.add(u)
        return urls
    except MySQLError as e:
        _db.reconnect()
        raise e
    finally:
        c.close()


def get_urls_from_app():
    return _get_urls_from_db('app', 'download_link')


def get_urls_from_apk_links():
    return _get_urls_from_db('apk_links', 'link')


def _get_urls_from_db(table, column_name):
    lastid_file = '/var/app/data/MarketSearchCrawler/incrementupdate-last_app_id.%s' % table
    dirname = os.path.dirname(lastid_file)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    lastid = None
    if os.path.exists(lastid_file):
        lines = [line.strip() for line in file(lastid_file)]
        for line in lines:
            if line.isdigit() and int(line):
                lastid = int(line)
                break
    if not lastid:
        sql = 'select id from %s order by id desc limit 2000, 1' % table
        c = _db.cursor()
        c.execute(sql)
        result = c.fetchone()
        if result:
            lastid = result[0]
        else:
            lastid = 0
        with open(lastid_file, 'w') as f:
            f.write(str(lastid))

    sql = 'select %s, id from %s where id > %%s order by id asc' % (column_name, table)
    c = _db.cursor()
    c.execute(sql, (lastid, ))
    result = c.fetchall()
    urls = [ul[0] for ul in result]
    if urls:
        lastid = result[-1][1]
        with open(lastid_file, 'w') as f:
            f.write(str(lastid))
    return urls

def add_urls_to_rabbitmq(urls, start=0):
    try:
        pc = pika.BlockingConnection(pika.ConnectionParameters(**settings.RABBITMQ['incrementupdate_urls']))
        c = pc.channel()
        c.queue_declare(queue='incrementupdate_urls', durable=True)
    except:
        time.sleep(1)
        add_urls_to_rabbitmq(urls, start)
        return
    start = start if start >= 0 else 0
    for i in range(start, len(urls)):
        u = urls[i]
        try:
            logger.i('will add url: %s' % u)
            c.basic_publish(exchange='', routing_key='incrementupdate_urls',
                            body=u, properties=pika.BasicProperties(delivery_mode=2))
        except Exception as e:
            logger.e('add url: %s failed' % u)
            add_urls_to_rabbitmq(urls, i-20)
            return


def main(url_file=None):
    if url_file:
        add_urls_to_rabbitmq([line.strip() for line in file(url_file) if line.strip()])
    else:
        add_urls_to_rabbitmq(get_urls_from_app())
        add_urls_to_rabbitmq(get_urls_from_apk_links())


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()


