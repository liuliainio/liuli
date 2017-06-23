#-*- coding: utf-8 -*-
'''
Created on Sep 12, 2013

@author: gmliao
'''
import pika


DATABASES = {
    'default': ['localhost', 'root', '1111', 'market']
}

REDIS = {
    'interception': {
        'host': 'localhost',
        'port': 6379,
        'db': 0,
    },
}


RABBITMQ = {
    'interception_download_urls': {
        'host': 'localhost',
        'port': 5672,
        'credentials': pika.credentials.PlainCredentials('interception', 'inter'),
    },
    'incrementupdate_urls': {
        'host': 'localhost',
        'port': 5672,
        'credentials': pika.credentials.PlainCredentials('interception', 'inter'),
    },
    'incrementupdate_update': {
        'host': 'localhost',
        'port': 5672,
        'credentials': pika.credentials.PlainCredentials('interception', 'inter'),
    },
    'verification_ids': {
        'host': 'localhost',
        'port': 5672,
        'credentials': pika.credentials.PlainCredentials('interception', 'inter'),
    }
}


INTERCEPTION_WORKER = {
    'thread_num': 2,
}

VERIFICATION_WORKER = {
    'thread_num': 2,
}

AAPT_PATH = 'aapt'
