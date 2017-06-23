#-*- coding: utf-8 -*-
'''
Created on Sep 12, 2013

@author: gmliao
'''


from _mysql_exceptions import MySQLError
from crawler import settings
from services.db import MySQLdbWrapper
from threading import Thread
from utils.net import Net
import os
import pika
import re
import signal
import threading
import time
import datetime
import urllib2
import shutil
from utils import logutils

logger = logutils.config_logger(__name__, '/var/app/log/MarketSearchCrawler/incrementupdate-urls.log')

_db = threading.local()

def get_db():
    if hasattr(_db, 'db'):
        return _db.db
    else:
        _db.db = MySQLdbWrapper()
        return _db.db


def get_total_seconds(td):
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 1e6) / 1e6


def need_to_handle(url):
    try:
        c = get_db().cursor()
        sql = '''
        select url, hash, error_times, updated_at from url_hash where url=%s
        '''
        logger.debug(sql % (url))
        c.execute(sql, (url, ))
        get_db().conn.commit()
        ret = c.fetchone()
        if not ret:
            return True
        elif ret[1]:
            return False
        elif ret[2] < 5 and get_total_seconds(datetime.datetime.now() - ret[3]) > 120:
            return True
        else:
            return False
    except MySQLError:
        get_db().reconnect()
        return True
    finally:
        c.close()


def insert_url(url):
    sql = 'insert ignore into url_hash(url, updated_at) values (%s, now())'
    try:
        c = get_db().cursor()
        logger.debug(sql % (url))
        c.execute(sql, (url, ))
        get_db().conn.commit()
    except MySQLError as e:
        logger.exception('update db failed: %s', e)
        get_db().reconnect()
        raise e
    finally:
        c.close()


def get_package_hash(file_path):
    command = 'md5sum %s' % file_path
    package_hash = os.popen(command).read().split()[0]
    return package_hash


def handle(url):
    insert_url(url)
    try:
        if not os.path.exists('/tmp/incrementupdate/'):
            os.makedirs('/tmp/incrementupdate/')
    except:
        pass
    filename = '/tmp/incrementupdate/incrementupdate-urls-%s-%s' % (os.getpid(), threading.current_thread().name)
    successdownload = False
    successhash = False
    with open(filename, 'wb') as f:
        logger.info('download start: file=%s, url=%s' % (filename, url))
        try:
            r = None
            start = time.time()
            request = urllib2.Request(url)
            request.add_header('Accept-encoding', 'gzip')
            request.add_header(
                'User-agent',
                'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_2; en-US) AppleWebKit/533.3 (KHTML, like Gecko) Chrome/5.0.354.0 Safari/533.3')
            r = urllib2.urlopen(request, timeout=10)
            shutil.copyfileobj(r, f)
            timespend = time.time() - start
            logger.info('download finished: file=%s, url=%s, filesize=%s, timespend=%ss' % (filename, url, os.path.getsize(filename), timespend))
            r.close()
            successdownload = True
        except Exception as e:
            logger.exception(e)
            logger.info('download error: file=%s, url=%s, err=%s' % (filename, url, e))
            if r:
                try:
                    r.close()
                except:
                    pass

    if successdownload:
        try:
            hash = get_package_hash(filename)
            successhash = True
        except Exception as e:
            logger.exception('get_package_hash for failed. file=%s, error=%s', filename, e)

    if os.path.exists(filename):
        try:
            os.remove(filename)
        except Exception as e:
            logger.exception('remove file failed: file=%s, error=%s', filename, e)

    if successhash:
        update_urlhash(url, hash=hash, last_download_time=timespend)
    else:
        update_urlhash(url, error=True)


def update_urlhash(url, hash=None, last_download_time=None, error=False):
    conds = ['updated_at=now()']
    if hash:
        conds.append("hash='%s'" % hash)
    if last_download_time:
        conds.append("last_download_time=%s" % last_download_time)
    if error:
        conds.append("error_times=error_times+1")
    sql = 'update url_hash set %s where url=%%s' % ','.join(conds)
    try:
        c = get_db().cursor()
        logger.debug(sql % (url))
        c.execute(sql, (url, ))
        get_db().conn.commit()
    except MySQLError as e:
        logger.exception('update db failed: %s', e)
        get_db().reconnect()
        raise e
    finally:
        c.close()


def reform_url(url):
    can_remove_param_hosts = ['118.123.97.191', 'download.taobaocdn.com',
                              'download.alipay.com', 'bs.baidu.com', 'cache.3g.cn',
                              'gamecache.3g.cn', 'a4.img.3366.com', 'apps.wandoujia.com',
                              '[0-9]+.[0-9]+.[0-9]+.[0-9]+/down.myapp.com']
    r = re.compile('^http://(%s)/.*.apk\?.*$' % '|'.join(can_remove_param_hosts))
    if r.match(url):
        ret = url[0: url.find('.apk?') + 4]
        logger.i('reform url: %s to url: %s' % (url, ret))
        return ret
    else:
        return url


HOSTS_TO_IGNORE = ['fast.yingyonghui.com', 'ftp-apk.pconline.com.cn']
hosts_regex = re.compile('^https?://(%s)/.*$' % '|'.join(HOSTS_TO_IGNORE))


def process(url):
    logger.info('process url: %s', url)
    if hosts_regex.match(url):
        logger.info('ignore url: %s' % url)
        return
    if need_to_handle(url):
        handle(url)
        logger.info('success process url: %s', url)
    else:
        logger.info('url does not need to be handled: %s', url)


def callback(ch, method, properties, body):
    url = body
    try:
        process(url)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.exception('process url failed, readd to rabbitmq. url=%s, error=%s', url, e)
        try:
            ch.basic_publish(exchange='', routing_key='incrementupdate_urls',
                             body=url, properties=pika.BasicProperties(delivery_mode=2))
        except Exception as e:
            logger.exception('readd to rabbitmq failed. url=%s, error=%s', url, e)


rmq_channels = []
pikas = []
should_stop = False
max_fail_times = 5


def run():
    logger.info('rmq_channel.start_consuming')
    _pika = None
    rmq_channel = None
    fail_times = 0
    while True and not should_stop and fail_times < max_fail_times:
        try:
            _pika = pika.BlockingConnection(
                pika.ConnectionParameters(**settings.RABBITMQ['incrementupdate_urls']))
            pikas.append(_pika)
            rmq_channel = _pika.channel()
            rmq_channel.queue_declare(queue='incrementupdate_urls', durable=True)
            rmq_channel.basic_qos(prefetch_count=1)
            rmq_channel.basic_consume(callback, queue='incrementupdate_urls')
            rmq_channels.append(rmq_channel)
            rmq_channel.start_consuming()
        except Exception as e:
            fail_times = fail_times + 1
            logger.exception('error consuming: %s' % e)
            if rmq_channel in rmq_channels:
                try:
                    rmq_channel.stop_consuming()
                    rmq_channel.close()
                except:
                    pass
                rmq_channels.remove(rmq_channel)
            if _pika in pikas:
                try:
                    _pika.close()
                except:
                    pass
                pikas.remove(_pika)
            time.sleep(5)


def graceful_exit(*args, **kargs):
    logger.info('request rabbit_consumer stop(%s, %s). stopping...' % (args, kargs))
    global should_stop
    should_stop = True
    for c in rmq_channels:
        try:
            c.stop_consuming()
            c.close()
        except Exception as e:
            logger.exception('stop_consuming failed: %s' % e)
    for p in pikas:
        try:
            p.close()
        except Exception as e:
            logger.exception('close rabbit connection failed: %s' % e)

signal.signal(signal.SIGINT, graceful_exit)
signal.signal(signal.SIGTERM, graceful_exit)

def start():
    threads = []
    for i in range(settings.INTERCEPTION_WORKER['thread_num']):
        t = Thread(target=run, name='incrementupdate_urls-rabbitmq-consumer-%s' % i)
        t.setDaemon(True)
        t.start()
        threads.append(t)

    while True:
        if not any([t.isAlive() for t in threads]):
            break
        else:
            time.sleep(1)


if __name__ == '__main__':
    start()
