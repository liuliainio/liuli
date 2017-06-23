#-*- coding: utf-8 -*-
'''
Created on Sep 12, 2013

@author: gmliao
'''


from _mysql_exceptions import MySQLError
from crawler import settings
from services.db import MySQLdbWrapper
from threading import Thread
from utils.logger import logger
from utils.net import Net
import os
import pika
import re
import redis
import signal
import threading
import time


_redis = redis.Redis(**settings.REDIS['interception'])


def parse_apk(filepath):
    command = "%s dump badging %s" % (settings.AAPT_PATH, filepath)
    logger.d('execute command: %s' % command)
    package_name = ''
    sdk_version = ''
    version_name = ''
    version_code = 0
    lines = os.popen(command).readlines()
    for line in lines:
        values = line.split(":", 1)
        if len(values) < 2:
            continue

        k = values[0].strip().lower()
        v = values[1].strip()
        if k == "package":
            m = re.match(r"name='(.+)' versionCode='(\d*)' versionName='(.*)'", v)
            if m:
                package_name = m.group(1)
                version_code = m.group(2)
                version_name = m.group(3)
            else:
                print "fail to extract info from '%s'" % v
        elif k == "sdkversion":
            m = re.match(r"'(\d+)'", v)
            if m:
                sdk_version = m.group(1)
    return package_name, version_code, version_name, sdk_version


_db = MySQLdbWrapper()


def get_url(packagename, version_code):
    try:
        c = _db.cursor()
        sql = '''
        select id, avail_download_links from final_app
        where package_name=%s and version_code=%s and file_type='apk'
        '''
        logger.d(sql % (packagename, version_code))
        c.execute(sql, (packagename, version_code))
        ret = c.fetchone()
        if not ret:
            return None, None
        else:
            return ret
    except MySQLError:
        _db.reconnect()
    finally:
        c.close()


def update_finalapp(id, urls):
    sql = '''
    update final_app set avail_download_links=%s, updated_at=current_timestamp(),
    status=status&0xfffffffffffffff8 where id = %s
    '''
    logger.d(sql % (urls, id))
    try:
        c = _db.cursor()
        c.execute(sql, (urls, id))
        _db.conn.commit()
    except MySQLError:
        _db.reconnect()
    finally:
        c.close()


def reform_interception_url(url):
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


def handle_download_links(urls):
    accepted_domains = ["apkc.mumayi.com", "dl.coolapk.com", "qd.cache.baidupcs.com", "cdn6.down.apk.gfan.com",
                        "file.liqucn.com", "smsftp.3g.cn", "dldir1.qq.com", "a4.img.3366.com", "static.nduoa.com",
                        "download.taobaocdn.com", "wap.apk.anzhi.com", "cache.3g.cn", "bcscdn.baidu.com",
                        "file.m.163.com", "down5.game.uc.cn", "dl.m.duoku.com", "cdn.market.hiapk.com",
                        "gdown.baidu.com", "bs.baidu.com", ]
    # not_accepted_domains = ['hiapk.com', ]
    us = urls.split(' ')

    def get_domain(url):
        r = re.compile('http[s]*://([^/]+)/.*')
        m = r.match(url)
        if m:
            return m.groups()[0]
        return None

    us.reverse()
    for u in us:
        if get_domain(u) not in accepted_domains:
            logger.i('url too long, will remove %s' % u)
            us.remove(u)
            us.reverse()
            return ' '.join(us)


def reform_urls(urls):
    us = urls.split(' ')
    new_urls = set()
    new_urls_list = []
    for u in us:
        u = reform_interception_url(u)
        new_urls.add(u)
        new_urls_list.append(u)
    us = new_urls_list
    new_urls_list = []
    for u in us:
        if u in new_urls:
            new_urls_list.append(u)
    return ' '.join(new_urls_list)


def update_avail_download_links(packagename, version_code, url):
    logger.i('update_avail_download_links packagename: %s, version_code: %s, url: %s' %
             (packagename, version_code, url))
    id, urls = get_url(packagename, version_code)
    if urls and urls.find(url) != -1:
        logger.i('final app already has url: %s' % url)
        return
    elif not urls:
        logger.i('final app not found')
        return
    else:
        new_urls = '%s %s' % (urls, url)
        new_urls = reform_urls(new_urls)
        while len(new_urls) > 2048:
            new_urls1 = handle_download_links(new_urls)
            if new_urls1 == new_urls:
                break
            new_urls = new_urls1
        if len(new_urls) > 2048:
            logger.e('new url too long: %s, will not process.' % new_urls)
            return
        update_finalapp(id, new_urls)


HOSTS_TO_IGNORE = ['fast.yingyonghui.com', 'ftp-apk.pconline.com.cn']
hosts_regex = re.compile('^https?://(%s)/.*$' % '|'.join(HOSTS_TO_IGNORE))


def process(url):
    logger.i('process url: %s' % url)
    if hosts_regex.match(url):
        logger.i('ignore url: %s' % url)
        return
    filepath = '/tmp/interception_%s_%s.apk' % (os.getpid(),
                                                threading.current_thread().name)
    Net.download(url, filepath)
    package_name, version_code, version_name, sdk_version = parse_apk(filepath)
    update_avail_download_links(package_name, version_code, url)


def callback(ch, method, properties, body):
    url = body
    queue_name_running = 'downloadurls_running'
    queue_name_success = 'downloadurls_success'
    queue_name_failed = 'downloadurls_failed'

    if _redis.hexists(queue_name_success, url):
        ch.basic_ack(delivery_tag=method.delivery_tag)
    elif _redis.hexists(queue_name_failed, url):
        ch.basic_ack(delivery_tag=method.delivery_tag)
    elif _redis.hexists(queue_name_running, url):
        _redis.hincrby(queue_name_running, url, 1)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    else:
        _redis.hset(queue_name_running, url, 0)
        try:
            process(url)
            _redis.hdel(queue_name_running, url)
            _redis.hset(queue_name_success, url, 0)
        except Exception as e:
            logger.e('process url(%s) failed: %s' % (url, e))
            _redis.hset(queue_name_failed, url, 0)
        ch.basic_ack(delivery_tag=method.delivery_tag)


rmq_channels = []
pikas = []
should_stop = False
max_fail_times = 5


def run():
    logger.i('rmq_channel.start_consuming')
    _pika = None
    rmq_channel = None
    fail_times = 0
    while True and not should_stop and fail_times < max_fail_times:
        try:
            _pika = pika.BlockingConnection(
                pika.ConnectionParameters(**settings.RABBITMQ['interception_download_urls']))
            pikas.append(_pika)
            rmq_channel = _pika.channel()
            rmq_channel.queue_declare(queue='downloadurls', durable=True)
            rmq_channel.basic_qos(prefetch_count=1)
            rmq_channel.basic_consume(callback, queue='downloadurls')
            rmq_channels.append(rmq_channel)
            rmq_channel.start_consuming()
        except Exception as e:
            fail_times = fail_times + 1
            logger.e('error consuming: %s' % e)
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
    logger.i('request rabbit_consumer stop(%s, %s). stopping...' % (args, kargs))
    global should_stop
    should_stop = True
    for c in rmq_channels:
        try:
            c.stop_consuming()
            c.close()
        except Exception as e:
            logger.e('stop_consuming failed: %s' % e)
    for p in pikas:
        try:
            p.close()
        except Exception as e:
            logger.e('close rabbit connection failed: %s' % e)

signal.signal(signal.SIGINT, graceful_exit)
signal.signal(signal.SIGTERM, graceful_exit)


def start():
    threads = []
    for i in range(settings.INTERCEPTION_WORKER['thread_num']):
        t = Thread(target=run, name='rabbitmq-consumer-%s' % i)
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
