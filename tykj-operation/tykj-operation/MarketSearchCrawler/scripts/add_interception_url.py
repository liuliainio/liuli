#-*- coding: utf-8 -*-
'''
Created on Sep 13, 2013


you should allow host to connect to rabbitmq first.
At 182.140.141.13: sudo iptables -I INPUT 13 -s {IP}/32 -p tcp -m state --state NEW -m tcp --dport 5672 -j ACCEPT

@author: gmliao
'''

import sys
import traceback
import datetime
reload(sys)
sys.setdefaultencoding('utf-8')

import pika
import re

RABBITMQ = {
    'interception_download_urls': {
        'host': '182.140.141.13',
        'port': 5672,
        'credentials': pika.credentials.PlainCredentials('interception', 'inter'),
    }
}

r = re.compile('.*([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}).*download_url=([^,]*),.*')


def minutes_begin(d):
    return datetime.datetime.strptime('%s:00' % (d.strftime('%Y%m%d %H:%M')), '%Y%m%d %H:%M:%S')

time_from = minutes_begin(datetime.datetime.now() - datetime.timedelta(seconds=60))
time_to = minutes_begin(datetime.datetime.now())


def get_url(line):
    m = r.match(line)
    try:
        if m:
            d, u = m.groups()
            d = datetime.datetime.strptime(d, '%Y-%m-%d %H:%M:%S')
            if d > time_from and d <= time_to:
                return u
            return None
        return None
    except Exception as e:
        print u're match for line(%s) failed: %s' % (line, e)
        return None

if __name__ == '__main__':
    urls = []
    for line in sys.stdin:
        u = get_url(line)
        if u:
            urls.append(u)
    print 'will add urls: %s' % urls
    pc = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ['interception_download_urls']))
    c = pc.channel()
    c.queue_declare(queue='downloadurls', durable=True)
    for u in urls:
        try:
            c.basic_publish(exchange='', routing_key='downloadurls',
                            body=u, properties=pika.BasicProperties(delivery_mode=2))
        except Exception as e:
            print 'add url: %s failed' % u
            print traceback.format_exc()
    pc.close()
