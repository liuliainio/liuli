#-*- coding: utf-8 -*-
'''
Created on Sep 12, 2013

@author: gmliao
'''
from crawler import settings
import MySQLdb


class MySQLdbWrapper:

    conn = None

    def connect(self):
        self.conn = MySQLdb.connect(settings.DATABASES['default'][0], settings.DATABASES['default'][1],
                                    settings.DATABASES['default'][2], settings.DATABASES['default'][3],
                                    charset='utf8', use_unicode=True)
        #self.conn = MySQLdb.connect('localhost', 'root', '1111', 'market')
        self.conn.set_character_set('utf8')

    def reconnect(self):
        self.conn = None

    def cursor(self):
        try:
            if not self.conn:
                self.connect()
            return self.conn.cursor()
        except MySQLdb.OperationalError:
            self.connect()
            return self.conn.cursor()
