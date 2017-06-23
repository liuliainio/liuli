#-*- coding: utf-8 -*-
'''
Created on Sep 13, 2013


you should allow host to connect to rabbitmq first.
At 182.140.141.13: sudo iptables -I INPUT 13 -s {IP}/32 -p tcp -m state --state NEW -m tcp --dport 5672 -j ACCEPT

@author: gmliao
'''

from crawler import settings
import datetime
import pika
import sys
import traceback

reload(sys)
getattr(sys, 'setdefaultencoding')('utf-8')

_queue_name = 'verification_ids'


def minutes_begin(d):
    return datetime.datetime.strptime('%s:00' % (d.strftime('%Y%m%d %H:%M')), '%Y%m%d %H:%M:%S')


time_from = minutes_begin(datetime.datetime.now() - datetime.timedelta(seconds=60))
time_to = minutes_begin(datetime.datetime.now())


def parse_args():
    try:
        args = sys.argv[1:]
        ret = {}
        for arg in args:
            k, v = arg.split('=')
            ret[k] = v
        return ret
    except Exception:
        traceback.print_exc()
        print '\n'
        help()
        sys.exit(1)


def help():
    print 'usage: %s ids=1,2,3...' % __file__


if __name__ == '__main__':
    args = parse_args()
    if not 'ids' in args:
        help()
        sys.exit(1)

    ids = [int(id) for id in args['ids'].split(',')]
    print 'will add ids: %s' % ids
    pc = pika.BlockingConnection(pika.ConnectionParameters(**settings.RABBITMQ['verification_ids']))
    c = pc.channel()
    c.queue_declare(queue=_queue_name, durable=True)
    for id in ids:
        try:
            c.basic_publish(exchange='', routing_key=_queue_name,
                            body=str(id), properties=pika.BasicProperties(delivery_mode=2))
        except Exception as e:
            print 'add id: %s failed' % id
            print traceback.format_exc()
    pc.close()
