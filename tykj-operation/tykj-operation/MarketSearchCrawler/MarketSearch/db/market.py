'''
Created on Jun 1, 2011

@author: yan
'''
from MarketSearch import service
from MarketSearch.gen.ttypes import Status, LinkStatus, LinkType
from MarketSearch.utils import log_error, log_info, get_epoch_datetime
from redis_queue import Queue
import MySQLdb
import string

_connections = {}
_conn = None
_table_dic = {
    'iphone.91.com': 'app_ios',
    'ipad.91.com': 'app_ios',
    'iphone.kuaiyong.com': 'app_ios',
    'ipad.kuaiyong.com': 'app_ios',
    '91.com': 'apt',
    'zhuti.xiaomi.com': 'apt',
    'image.xiaomi.com': 'img',
    'image.91.com': 'img',
    'market.android.com': 'app',
    'as.baidu.com': 'app',
    'update.as.baidu.com': 'app',
    'wandoujia.com': 'app',
    'update.wandoujia.com': 'app',
    'zhushou.360.cn': 'app',
    'update.zhushou.360.cn': 'app',
    'hiapk.com': 'app',
    'update.hiapk.com': 'app',
    'goapk.com': 'app',
    'update.goapk.com': 'app',
    'appchina.com': 'app',
    'update.appchina.com': 'app',
    'myapp.com': 'app',
    'update.myapp.com': 'app',
    'nduoa.com': 'app',
    'update.nduoa.com': 'app',
    'mumayi.com': 'app',
    'update.mumayi.com': 'app',
    'tripadvisor.com': 'tripadvisor',
    'yelp.com': 'yelp',
    'itunes.apple.com': 'apple',
    'yelp.com': 'yelp',
    'youtube.com': 'youtube',
    'kuaiyong.com': 'app_ios',
    'ipa.91.com': 'app_ios',
    'itunes.apple.com': 'app_itunes',
}
_link_monitor_table = 'link_monitor'

_queue = None
_queue_name = 'image_queue'


def config(host, user, password, db):
    global _conn
    _conn = _get_connection(host, user, password, db)


def init_queue(host, port, password):
    global _queue
    _queue = Queue(_queue_name, host=host, port=port, password=password)


def push_image_url(url):
    _queue.append(url)


def _get_connection(host, user, password, db):
    key = host
    conn = None
    if key in _connections:
        conn = _connections[key]
    else:
        conn = MySQLdb.connect(host, user, password, db)
        conn.set_character_set('utf8')
        _connections[key] = conn
    return conn


def remove_app(source_link, name):
    service.report_status([LinkStatus(source_link, name, Status.FAIL, LinkType.UNKNOWN)])
#    try:
#        cursor = _conn.cursor()

#        sql = "DELETE FROM " + _table_dic[name] + " WHERE source_link = %s"
#        cursor.execute(sql, source_link)

#        _conn.commit()
#
#    except MySQLdb.Error, e:
#        log_error(e)
#    finally:
#        cursor.close()


def save_download_link(item):
    if not item:
        return
    try:
        c = _conn.cursor()
        sql = 'insert ignore into apk_links(link, updated_at) values (%s, now())'
        c.execute(sql, (item['url'], ))
        _conn.commit()
    except Exception as e:
        log_error(e)
    finally:
        c.close()


def save_app(item, name):
    if not item:
        return
    try:
        cursor = _conn.cursor()

        # record last_crawl time
        item['last_crawl'] = get_epoch_datetime()
        if name == 'play.google.com':
            save_final_app(cursor, item)
        else:
            _upsert_item(cursor, item, _table_dic.get(name, 'app'))
        _conn.commit()
    except Exception as e:
        log_error(e)
    finally:
        cursor.close()


def save_final_app(cursor, item):
    sql = "INSERT IGNORE INTO final_app_meta (" + string.join(item.fields.keys(), ',') + \
          ") values (" + string.join(["%s"] * len(item.fields.keys()), ',') + \
          ")"
    values = [item.get(key) for key in item.fields.keys()]
    cursor.execute(sql, tuple(values))
    print 'INSERT APP [%s]%s' % (item['source'], item['name'])
    log_info('INSERT APP [%s]%s' % (item['source'], item['name']))


def _upsert_item(cursor, item, table):
    log_info("**************into mysql ******************")
    if item['source'] == 'itunes.apple.com':
        sql = "select * from " + table + " where version=%s and app_id=%s"
        cursor.execute(sql, (item['version'], item['app_id']))
        result = cursor.fetchone()
        if result:
            return
    if 'publish_date' in item:
        sql = "select publish_date from " + table + " where source_link = '%s' " % item['source_link']
        cursor.execute(sql)
        publish_date = cursor.fetchone()
        if publish_date and publish_date[0] >= item['publish_date']:
            log_info('INSERT APP IGNORE [%s]%s' % (item['source'], item['name']))
            return
    if table == 'app':
        if 'version' in item and 'source_link' in item:
            item['source_link'] = item['source_link']
    sql = "INSERT INTO " + table + " (" + string.join(item.fields.keys(), ',') + \
          ") values (" + string.join(["%s"] * len(item.fields.keys()), ',') + \
          ") ON DUPLICATE KEY UPDATE tag = null, " + \
        string.join([key + "=%s" for key in item.fields.keys() if item.get(key)], ',')
    values = [item.get(key) for key in item.fields.keys()] + \
             [item.get(key) for key in item.fields.keys() if item.get(key)]

    cursor.execute(sql, tuple(values))
    print 'INSERT APP [%s]%s' % (item['source'], item['name'])
    log_info('INSERT APP [%s]%s' % (item['source'], item['name']))


def report_link(source, catetory, link, description=''):
    try:
        cursor = _conn.cursor()

        insert_sql = "INSERT INTO %s (source, category, link, description, create_time) VALUES('%s', '%s', '%s', '%s', %s)" % \
            (_link_monitor_table, source, catetory, link, description, get_epoch_datetime())
        cursor.execute(insert_sql)
        _conn.commit()
    except MySQLdb.Error as e:
        log_error(e)
    finally:
        cursor.close()


def get_apple_id(app_id):
    try:
        cursor = _conn.cursor()
        sql = "SELECT apple_id FROM app_itunes where app_id = %s"
        cursor.execute(sql, app_id)
        result = cursor.fetchone()
        if not result:
            cursor = _conn.cursor()
            sql = "SELECT username FROM apple_account ORDER BY app_num ASC limit 1"
            cursor.execute(sql)
            result = cursor.fetchone()
        sql = "UPDATE apple_account set app_num = app_num + 1 WHERE username=%s"
        cursor.execute(sql, result[0])
        _conn.commit()
        return result[0]
    except MySQLdb.Error as e:
        log_error(e)
    finally:
        cursor.close()


def get_category(app_id):
    try:
        cursor = _conn.cursor()
        sql = "SELECT cate_name FROM itunes_game_cate where app_id = %s"
        cursor.execute(sql, app_id)
        result = cursor.fetchone()
        if not result:
            return u'\u52a8\u4f5c\u6e38\u620f'
        else:
            return result[0]
    except MySQLdb.Error as e:
        log_error(e)
    finally:
        cursor.close()

