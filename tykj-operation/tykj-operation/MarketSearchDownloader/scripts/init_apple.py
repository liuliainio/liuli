# coding=utf-8
import os
import MySQLdb
import random
from hashlib import md5
from BeautifulSoup import BeautifulSoup
import hashlib


class MySQLdbWrapper:

    conn = None

    def connect(self):
        self.conn = MySQLdb.connect('192.168.130.77', 'dev_market', 'market_dev_pwd', 'market')
        self.conn.set_character_set('utf8')

    def cursor(self):
        try:
            if not self.conn:
                self.connect()
            return self.conn.cursor()
        except MySQLdb.OperationalError:
            self.connect()
            return self.conn.cursor()

_db = MySQLdbWrapper()

for line in open('apple_account.txt', 'r').readlines():
    username = line.split()[0]
    password = line.split()[1]
    cursor = _db.cursor()
    sql = "insert into apple_account (username,password,app_num)  values (%s,%s,%s)"
    cursor.execute(sql, (username, password, 0))
    _db.conn.commit()
