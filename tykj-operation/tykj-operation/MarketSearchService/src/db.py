'''
Created on Jun 27, 2011

@author: yan
'''
import MySQLdb
import string
from platform import node
from scheduler import prepare_link_item, get_last_crawl_limit, get_priority_limit, get_update_crawl_limit
from utils import get_epoch_datetime
import datetime

_link_table = 'new_link'
_DEFAULT_LINK_BATCH_SIZE = 300

table_dic = {'ipa.kuaiyong.com': 'app_ios',
             'ipa.91.com': 'app_ios',
             'itunes.apple.com': 'app_itunes',
             'as.baidu.com': 'app',
             'wandoujia.com': 'app',
             'zhushou.360.cn': 'app',
             'goapk.com': 'app',
             'hiapk.com': 'app',
             'appchina.com': 'app',
             'myapp.com': 'app',
             'nduoa.com': 'app',
             'mumayi.com': 'app',
             '91.com': 'apt',
             'zhuti.xiaomi.com': 'apt',
             'lock.xiaomi.com': 'apt',
             'icon.xiaomi.com': 'apt',
             'font.xiaomi.com': 'apt',
             'wallpaper.xiaomi.com': 'img',
             'image.91.com': 'img',
             }

class MySQLdbWrapper:

    conn = None

    def connect(self):
        if node() in ['gmliaovm']:
            self.conn = MySQLdb.connect('localhost', 'root', '1111', 'market')
        else:
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


def get_links(source, pendings):
    size_limit = max(_DEFAULT_LINK_BATCH_SIZE - pendings, 0)
    if size_limit == 0:
        return None

    try:
        cursor = _db.cursor()

        crawl_limit = str(get_last_crawl_limit())
        priority_limit = get_priority_limit()

        #remove the distributed links(last_crawl=2) avoid duplicate
        sql = 'SELECT link,id FROM ' + _link_table + ' WHERE source = %s AND last_crawl < %s AND last_crawl <> 2 AND priority <= %s ORDER BY ABS(priority) ASC, last_crawl ASC limit %s'
        cursor.execute(sql, (source, crawl_limit, priority_limit, size_limit))
        result = cursor.fetchall()
        id_set = [tup[1] for tup in result]
        #update last_crawl to 2 (2: the distributed links)
        if id_set:
            update_sql = 'UPDATE ' + _link_table + ' SET last_crawl = %s WHERE id in ("%s")' % ('2','","'.join(id_set))
            cursor.execute(update_sql)
        _db.conn.commit()
        return result
    except MySQLdb.Error, e:
        print e
    finally:
        cursor.close()

def get_update_links(source, pendings):
    size_limit = max(_DEFAULT_LINK_BATCH_SIZE - pendings, 0)
    if size_limit == 0:
        return None

    try:
        cursor = _db.cursor()

        crawl_limit = str(get_update_crawl_limit())
        priority_limit = get_priority_limit()

        sql = 'SELECT link,id FROM update_link WHERE source = %s AND last_crawl < %s AND last_crawl <> 2 AND priority <= %s ORDER BY ABS(priority) ASC, last_crawl ASC limit %s'
        print datetime.datetime.now(), sql
        cursor.execute(sql, (source, crawl_limit, priority_limit, size_limit))
        result = cursor.fetchall()
        id_set = [tup[1] for tup in result]
        if id_set:
            update_sql = 'UPDATE update_link SET last_crawl = %s WHERE id in ("%s")' % ('2','","'.join(id_set))
            print datetime.datetime.now(), sql
            cursor.execute(update_sql)
        _db.conn.commit()
        return result
    except MySQLdb.Error, e:
        print e
    finally:
        cursor.close()

def get_apk_links(source, pendings):
    size_limit = max(_DEFAULT_LINK_BATCH_SIZE - pendings, 0)
    if size_limit == 0:
        return None

    try:
        cursor = _db.cursor()

        #remove the distributed links(last_crawl=2) avoid duplicate
        sql = 'SELECT source_link,download_link,apk_size,id FROM ' + table_dic[source] + ' WHERE source = %s and tag is NULL order by last_crawl asc limit %s'
        print datetime.datetime.now(), sql, (source, size_limit)
        cursor.execute(sql, (source, size_limit))
        result = cursor.fetchall()
        id_set = [str(tup[3]) for tup in result]
#        #update last_crawl to 2 (2: the distributed links)
        if id_set:
            update_sql = 'UPDATE ' + table_dic[source] + ' SET tag = %s WHERE  id in (%s)' % ('2',','.join(id_set))
            print datetime.datetime.now(), sql
            cursor.execute(update_sql)
        _db.conn.commit()
        return result
    except MySQLdb.Error, e:
        print e
    finally:
        cursor.close()

def get_update_apk_links(source, pendings):
    size_limit = max(_DEFAULT_LINK_BATCH_SIZE - pendings, 0)
    if size_limit == 0:
        return None

    try:
        cursor = _db.cursor()

        #remove the distributed links(last_crawl=2) avoid duplicate
        sql = 'SELECT source_link,download_link,apk_size,id FROM ' + table_dic[source] + ' WHERE source = %s and tag is NULL order by last_crawl desc limit %s'
        print datetime.datetime.now(), sql, (source, size_limit)
        cursor.execute(sql, (source, size_limit))
        result = cursor.fetchall()
        id_set = [str(tup[3]) for tup in result]
#        #update last_crawl to 2 (2: the distributed links)
        if id_set:
            update_sql = 'UPDATE ' + table_dic[source] + ' SET tag = %s WHERE  id in (%s)' % ('2',','.join(id_set))
            print datetime.datetime.now(), sql
            cursor.execute(update_sql)
        _db.conn.commit()
        return result
    except MySQLdb.Error, e:
        print e
    finally:
        cursor.close()

def get_apk_files(source, pendings):
    size_limit = max(_DEFAULT_LINK_BATCH_SIZE - pendings, 0)
    if size_limit == 0:
        return None

    try:
        cursor = _db.cursor()

        #remove the distributed links(last_crawl=2) avoid duplicate
        sql = 'SELECT source_link,download_link,source,vol_id FROM entry WHERE source = %s and tag is NULL limit %s'
        print datetime.datetime.now(), sql
        cursor.execute(sql, (source, size_limit))
        result = cursor.fetchall()

        return result
    except MySQLdb.Error, e:
        print e
    finally:
        cursor.close()

def get_dup_apk_files(source, pendings):
    size_limit = max(_DEFAULT_LINK_BATCH_SIZE - pendings, 0)
    if size_limit == 0:
        return None

    try:
        cursor = _db.cursor()

        #remove the distributed links(last_crawl=2) avoid duplicate
        sql = 'SELECT source_link,download_link,source,vol_id FROM duplicate_apk WHERE source = %s and tag is NULL limit %s'
        cursor.execute(sql, (source, size_limit))
        result = cursor.fetchall()

        return result
    except MySQLdb.Error, e:
        print e
    finally:
        cursor.close()

def get_uniq_apk_files(source, pendings):
    size_limit = max(_DEFAULT_LINK_BATCH_SIZE - pendings, 0)
    if size_limit == 0:
        return None

    try:
        cursor = _db.cursor()

        sql = 'SELECT source_link,download_link,source,vol_id FROM unique_apk WHERE source = %s and tag is NULL limit %s'
        print datetime.datetime.now(), sql
        cursor.execute(sql, (source, size_limit))
        result = cursor.fetchall()

        return result
    except MySQLdb.Error, e:
        print e
    finally:
        cursor.close()

def update_links(status_list):
    try:
        cursor = _db.cursor()

        for item in status_list:
            insert_item = prepare_link_item(item, cursor, True)
            update_item = prepare_link_item(item, cursor, False)

            sql = 'INSERT INTO ' + _link_table + '(' + string.join(insert_item.keys(), ',') + \
                  ') values (' + string.join(['%s'] * len(insert_item.keys()), ',') + \
                  ') ON DUPLICATE KEY UPDATE ' + string.join([key + '=%s' for key in update_item.keys() if update_item[key]], ',')
            values = [insert_item[key] for key in insert_item.keys()] + [update_item[key] for key in update_item.keys() if update_item[key]]

            #print datetime.datetime.now(), sql
            cursor.execute(sql, tuple(values))
            _db.conn.commit()

    except MySQLdb.Error, e:
        print e
        print sql
    finally:
        cursor.close()

def update_update_links(status_list):
    try:
        cursor = _db.cursor()

        for item in status_list:
            insert_item = prepare_link_item(item, cursor, True)
            update_item = prepare_link_item(item, cursor, False)

            sql = 'INSERT INTO update_link (' + string.join(insert_item.keys(), ',') + \
                  ') values (' + string.join(['%s'] * len(insert_item.keys()), ',') + \
                  ') ON DUPLICATE KEY UPDATE ' + string.join([key + '=%s' for key in update_item.keys() if update_item[key]], ',')
            values = [insert_item[key] for key in insert_item.keys()] + [update_item[key] for key in update_item.keys() if update_item[key]]

            #print datetime.datetime.now(), sql, values
            cursor.execute(sql, tuple(values))
            _db.conn.commit()

    except MySQLdb.Error, e:
        print e
        print sql
    finally:
        cursor.close()


def update_apk_links(status_list):
    try:
        cursor = _db.cursor()

        for item in status_list:
            if item.status == 1:
                sql = 'UPDATE ' + table_dic[item.source] + ' set tag = %s where download_link = %s'
                #print datetime.datetime.now(), sql
                cursor.execute(sql, (get_epoch_datetime(), item.url))
                _db.conn.commit()
                sql = 'INSERT INTO entry (source_link, download_link, source, file_name, vol_id) VALUES (%s, %s, %s, %s, %s)'
                #print datetime.datetime.now(), sql
                cursor.execute(sql, (item.source_link, item.url, item.source, item.file, item.vol_id))
                _db.conn.commit()
            else:
#                sql = 'UPDATE ' + table_dic[item.source] + ' set tag = %s where download_link = %s'
#                cursor.execute(sql, (item.status, item.url))
#                sql = 'UPDATE new_link SET last_crawl = 1,priority=6 where link=%s'
#                cursor.execute(sql, (item.source_link))
                sql = 'UPDATE ' + table_dic[item.source] + ' set tag = %s where download_link = %s'
                #print datetime.datetime.now(), sql
                cursor.execute(sql, (item.status, item.url))
                _db.conn.commit()
    except MySQLdb.Error, e:
        print e
        print sql
    finally:
        cursor.close()

def update_apk_files(status_list):
    try:
        cursor = _db.cursor()

        for item in status_list:
            if item.status == 1:
                sql = 'UPDATE entry set tag = %s where download_link = %s'
                #print datetime.datetime.now(), sql
                cursor.execute(sql, (1, item.url))
                sql = 'SELECT download_link FROM unique_apk where package_name = %s and version_code = %s'
                #print datetime.datetime.now(), sql
                cursor.execute(sql, (item.package_name, item.version_code))
                result = cursor.fetchone()
                if result and result[0] != item.url:
                    sql = 'INSERT INTO duplicate_apk (package_name, version_code, source_link, download_link, source, vol_id) ' + \
                    'VALUES (%s, %s, %s, %s, %s, %s)'
                    #print datetime.datetime.now(), sql
                    cursor.execute(sql, (item.package_name, item.version_code, item.source_link, item.url, item.source, item.vol_id))
                else:
                    sql = 'INSERT IGNORE INTO unique_apk (package_name, version_code, source_link, download_link, source, vol_id) ' + \
                    'VALUES (%s, %s, %s, %s, %s, %s)'
                    #print datetime.datetime.now(), sql
                    cursor.execute(sql, (item.package_name, item.version_code, item.source_link, item.url, item.source, item.vol_id))
                    print 'update_apk_files: ', (sql % (item.package_name, item.version_code, item.source_link, item.url, item.source, item.vol_id))
                _db.conn.commit()
            else:
                sql = 'UPDATE entry SET tag = %s where download_link = %s'
                #print datetime.datetime.now(), sql
                cursor.execute(sql, (item.status, item.url))
                _db.conn.commit()
    except MySQLdb.Error, e:
        print e
        print sql
    finally:
        cursor.close()

def update_dup_apk_files(status_list):
    try:
        cursor = _db.cursor()

        for item in status_list:
            sql = 'UPDATE duplicate_apk set tag = %s where download_link = %s'
            cursor.execute(sql, (item.status, item.url))
            _db.conn.commit()
    except MySQLdb.Error, e:
        print e
        print sql
    finally:
        cursor.close()

def update_uniq_apk_files(status_list):
    try:
        cursor = _db.cursor()

        for item in status_list:
            sql = 'UPDATE unique_apk set tag = %s, sig = %s where download_link = %s'
            cursor.execute(sql, (item.status, item.package_name , item.url))
            _db.conn.commit()
    except MySQLdb.Error, e:
        print e
        print sql
    finally:
        cursor.close()


def insert_apk_files(status_list):
    try:
        cursor = _db.cursor()
        for item in status_list:
            sql = 'UPDATE entry set tag = %s where download_link = %s'
            cursor.execute(sql, (item.status, item.url))
            sql = '''
            INSERT IGNORE INTO unique_apk 
                (package_name, version_code, source_link, download_link, source, 
                vol_id, sig, version, apk_size, min_sdk_version, screen_support, 
                is_break, file_type, platform, package_hash) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(sql, (item.package_name, item.version_code, item.source_link, 
                                 item.url, item.source, item.vol_id, item.signature, 
                                 item.version_name, item.apk_size, item.min_sdk_version, 
                                 item.screen_support, item.is_break, item.file_type, 
                                 item.platform, item.package_hash))
            print (sql % (item.package_name, item.version_code, item.source_link, 
                          item.url, item.source, item.vol_id, item.signature, 
                          item.version_name, item.apk_size, item.min_sdk_version, 
                          item.screen_support, item.is_break, item.file_type, 
                          item.platform, item.package_hash))
            _db.conn.commit()
    except MySQLdb.Error, e:
        print e
        print sql
    finally:
        cursor.close()

def remove_apk_files(status_list):
    try:
        cursor = _db.cursor()

        for item in status_list:
            sql = 'UPDATE entry set tag = %s where download_link = %s'
            cursor.execute(sql, (item.status, item.url))
            sql = 'INSERT INTO duplicate_apk (package_name, version_code, source_link, download_link, source, vol_id, tag) ' + \
                    'VALUES (%s, %s, %s, %s, %s, %s, %s)'
            cursor.execute(sql, (item.package_name, item.version_code, item.source_link, item.url, item.source, item.vol_id, item.status))
            _db.conn.commit()
    except MySQLdb.Error, e:
        print e
        print sql
    finally:
        cursor.close()
