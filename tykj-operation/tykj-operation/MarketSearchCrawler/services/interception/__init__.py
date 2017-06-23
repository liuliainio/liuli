#-*- coding: utf-8 -*-
'''
Created on Sep 11, 2013

@author: gmliao
'''

from services.interception import rabbitmq_consumer


def start_rabbitmq_consumer():
    rabbitmq_consumer.start()

