#-*- coding: utf-8 -*-
'''
Created on Sep 22, 2013

@author: gmliao
'''
from _mysql_exceptions import MySQLError
from crawler import settings
from services.db import MySQLdbWrapper
from threading import Thread
from utils.logger import logger
import datetime
import pika
import signal
import simplejson
import sys
import threading
import time
import urllib2


reload(sys)
getattr(sys, 'setdefaultencoding')('utf8')

_db = threading.local()
_queue_name = 'verification_ids'

logger.level = logger.LEVEL_INFO


def get_db():
    if hasattr(_db, 'db'):
        return _db.db
    else:
        _db.db = MySQLdbWrapper()
        return _db.db


class HeadRequest(urllib2.Request):

    def get_method(self):
        return 'HEAD'


def url404(url, url1=None):
    try:
        urllib2.urlopen(HeadRequest(url))
        return False
    except urllib2.HTTPError as e:
        return e.code == 404
    except Exception as e:
        logger.i('request url(%s) failed: %s' % (url, e))
        if url1:
            return url404(url1)
        else:
            return False


def get_url(id):
    try:
        c = get_db().cursor()
        sql = '''
        select file_path, vol_id from final_app
        where id=%s and file_type='apk'
        '''
        logger.d(sql % (id))
        c.execute(sql, (id))
        ret = c.fetchone()
        if not ret:
            return None, None
        else:
            return ret
    except MySQLError:
        get_db().reconnect()
    finally:
        c.close()


def update_finalapp_safe(id, tencent_safe, info):
    sql = '''
    insert into final_app_safe(final_app_id, last_verify_time, tencent_safe, info)
    values (%s, %s, %s, %s)
    on duplicate key update last_verify_time=%s, tencent_safe=%s, info=%s
    '''
    try:
        c = get_db().cursor()
        now = datetime.datetime.now()
        logger.d(sql % (id, now, tencent_safe, info, now, tencent_safe, info))
        c.execute(sql, (id, now, tencent_safe, info, now, tencent_safe, info))
        get_db().conn.commit()
    except MySQLError:
        get_db().reconnect()
    finally:
        c.close()


def post(url, data):
    req = urllib2.Request(url)
    # enable cookie
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    response = opener.open(req, data)
    return response.read()

download_host = '192.168.132.229'


def process(id):
    logger.i('process id: %s' % id)
    file_path, vol_id = get_url(id)
    if file_path:
        data = '{"authkey":"9ORmsDOAJ3zcD21w", "url":"http://estoredwnld7.189store.com/downloads/vol%s/%s"}' % \
            (vol_id, file_path)
        url = 'http://%s/vol%s/%s' % ('estoredwnld7.189store.com', vol_id, file_path)
        url1 = 'http://%s/vol%s/%s' % (download_host, vol_id, file_path)
        if url404(url, url1):
            logger.i('found app(id=%s) url(%s) 404' % (id, url))
            update_finalapp_safe(id, 4, '')
            return True
        tencent_url = 'https://api.scan.qq.com/browser/scan'
        ret = ''
        try:
            ret = post(tencent_url, data)
            ret = ret.replace('\r', '')
            ret = ret.replace('\n', '')
            ret = simplejson.loads(ret)
        except Exception as e:
            logger.e(u'ret format error: %s' % ret)
            raise e
        logger.d('tencent returns: %s' % simplejson.dumps(ret))
        if 'safetype' not in ret:
            raise 'error format: %s' % simplejson.dumps(ret)
        if ret['safetype'] == 'unknown':
            update_finalapp_safe(id, None, '')
            return False
        if ret['safetype'] == 'virus':
            logger.i('found app(id=%s) has virus.' % id)
            update_finalapp_safe(id, 0, simplejson.dumps(ret))
            return True
        if ret['safetype'] == 'lowrisk':
            logger.i('found app(id=%s) lowrisk.' % id)
            update_finalapp_safe(id, 2, simplejson.dumps(ret))
            return True
        if ret['safetype'] == 'midrisk':
            logger.i('found app(id=%s) midrisk.' % id)
            update_finalapp_safe(id, 3, simplejson.dumps(ret))
            return True
        if ret['safetype'] == 'safe':
            logger.i('found app(id=%s) safe.' % id)
            update_finalapp_safe(id, 1, '')
            return True
    else:
        logger.i('can not find id in db, ignore: %s' % id)
        return True


def callback(ch, method, properties, body):
    id = body
    try:
        if not process(id):
            logger.d('process id(%s) return False, add to queue')
            ch.basic_publish(exchange='', routing_key=_queue_name,
                             body=id, properties=pika.BasicProperties(delivery_mode=2))
    except Exception as e:
        logger.e('process id(%s) failed: %s' % (id, e))
        logger.d('process id(%s) return False, add to queue')
        ch.basic_publish(exchange='', routing_key=_queue_name,
                         body=id, properties=pika.BasicProperties(delivery_mode=2))
    ch.basic_ack(delivery_tag=method.delivery_tag)

rmq_channels = []
pikas = []
should_stop = False


def run():
    logger.i('rmq_channel.start_consuming')
    _pika = None
    rmq_channel = None
    fail_times = 0
    while True and not should_stop:
        try:
            _pika = pika.BlockingConnection(pika.ConnectionParameters(**settings.RABBITMQ['verification_ids']))
            pikas.append(_pika)
            rmq_channel = _pika.channel()
            rmq_channel.queue_declare(queue=_queue_name, durable=True)
            rmq_channel.basic_qos(prefetch_count=1)
            rmq_channel.basic_consume(callback, queue=_queue_name)
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
            time.sleep(5 * fail_times)


def graceful_exit(*args, **kargs):
    logger.i('request verification_consumer stop(%s, %s). stopping...' % (args, kargs))
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
    for i in range(settings.VERIFICATION_WORKER['thread_num']):
        t = Thread(target=run, name='verification-consumer-%s' % i)
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
