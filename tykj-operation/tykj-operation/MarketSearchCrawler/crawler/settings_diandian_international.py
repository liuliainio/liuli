#-*- coding: utf-8 -*-
'''
Created on Dec 13, 2013

@author: gmliao
'''
import pika

DATABASES = {
    'default': ['10.134.6.128', 'dev_market', 'market_dev_pwd', 'market_india']
}

REDIS = {
    'interception': {
        'host': '192.168.130.76',
        'port': 6379,
        'db': 0,
    },
}


RABBITMQ = {
    'interception_download_urls': {
        'host': '192.168.130.118',
        'port': 5672,
        'credentials': pika.credentials.PlainCredentials('interception', 'inter'),
    },
    'incrementupdate_urls': {
        'host': '192.168.130.118',
        'port': 5672,
        'credentials': pika.credentials.PlainCredentials('interception', 'inter'),
    },
    'incrementupdate_update': {
        'host': '192.168.130.118',
        'port': 5672,
        'credentials': pika.credentials.PlainCredentials('interception', 'inter'),
    },
    'verification_ids': {
        'host': '192.168.130.118',
        'port': 5672,
        'credentials': pika.credentials.PlainCredentials('interception', 'inter'),
    }
}
