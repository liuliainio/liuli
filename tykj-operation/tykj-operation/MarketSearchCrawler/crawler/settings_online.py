#-*- coding: utf-8 -*-
'''
Created on Sep 12, 2013

@author: gmliao
'''
import pika

DATABASES = {
    'default': ['192.168.130.77', 'dev_market', 'market_dev_pwd', 'market']
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


INTERCEPTION_WORKER = {
    'thread_num': 15,
}

VERIFICATION_WORKER = {
    'thread_num': 30,
}


AAPT_PATH = '/var/app/enabled/MarketSearchCrawler/scripts/aapt'
