# encoding=utf-8
import MySQLdb
from settings import DB_CONFIG

import logging
logger = logging.getLogger()


class MySQLdbWrapper:

    conn = None

    def connect(self):
        self.conn = MySQLdb.connect(DB_CONFIG['host'], DB_CONFIG['user'], DB_CONFIG['password'], DB_CONFIG['db'])
        self.conn.set_character_set('utf8')

    def cursor(self):
        try:
            if not self.conn:
                self.connect()
            return self.conn.cursor()
        except MySQLdb.OperationalError:
            self.connect()
            return self.conn.cursor()


def get_vols():
    try:
        _db = MySQLdbWrapper()
        cursor = _db.cursor()
        sql = 'SELECT id, total_kbytes, used_kbytes FROM vol'
        cursor.execute(sql)
        result = cursor.fetchall()
        return result
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()


def is_apk_exist(packageName, versionCode, file_type, is_break, key_url):
    try:
        _db = MySQLdbWrapper()
        cursor = _db.cursor()
        sql = 'SELECT download_link FROM unique_apk where package_name = %s and version_code = %s and file_type = %s and is_break = %s'
        cursor.execute(sql, (packageName, versionCode, file_type, is_break))
        result = cursor.fetchone()
        if result and result[0] != key_url:
            logger.info('apk_exist: %s %s %s %s' % (packageName, versionCode, file_type, is_break))
            return True
        else:
            return False
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()
