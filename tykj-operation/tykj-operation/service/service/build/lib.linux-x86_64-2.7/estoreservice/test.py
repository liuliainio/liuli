#-*- coding: utf-8 -*-
'''
Created on Nov 19, 2013

@author: gmliao
'''
from django.conf import settings
from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings
from estorecore.servemodels.app import AppMongodbStorage
from estorecore.servemodels.user import UserMongodbStorage
from estoreservice.utils.resp_code import ERROR_CODE_SUCCESS
import logging
import simplejson


logger = logging.getLogger('unit_test')

user_db = UserMongodbStorage(settings.MONGODB_CONF)
app_db = AppMongodbStorage(settings.MONGODB_CONF)


@override_settings(DEBUG=True)
class TestBase(TestCase):

    def setUp(self):
        TestCase.setUp(self)
        user_db._db.apikeys.update(
            {'apikey': 'testapikey'},
            {"apikey": "testapikey",
             "is_enable": True},
            True)

    def i(self, msg, *args, **kwargs):
        logger.info(msg, *args, **kwargs)

    def d(self, msg, *args, **kwargs):
        logger.debug(msg, *args, **kwargs)

    def w(self, msg, *args, **kwargs):
        logger.warn(msg, *args, **kwargs)

    def exp(self, msg, *args, **kwargs):
        logger.exception(msg, *args, **kwargs)

    def e(self, msg, *args, **kwargs):
        logger.error(msg, *args, **kwargs)

    def get_json(self, path, data):
        client = Client()
        resp = client.get(path, data)
        return simplejson.loads(resp.content)

    def assert_get_error_code(self, path, data, code):
        data = self.get_json(path, data)
        self.assertTrue(data['error_code'] == code,
                        'GET %s with %s must return error code: %s' % (path, data, code))

    def assert_get_data(self, path, data, func):
        data = self.get_json(path, data)
        self.assertTrue(data['error_code'] == ERROR_CODE_SUCCESS,
                        'GET %s with %s must return error code success' % (path, data))
        self.assertTrue(func(data['data']),
                        'GET %s with %s must return data tested success with func: %s' % (path, data, func))

    def post_json(self, path, data):
        client = Client()
        resp = client.post(path, data, CONTENT_TYPE='application/json')
        return simplejson.loads(resp.content)
