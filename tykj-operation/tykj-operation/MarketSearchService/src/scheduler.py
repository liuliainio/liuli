'''
Created on Jul 1, 2011

@author: yan
'''
import MySQLdb
from MarketSearch.gen.ttypes import Status, LinkType
from utils import get_epoch_datetime, get_str_md5


_CRAWL_PRIORITY_MISSING = 12
_CRAWL_PRIORITY_FAILED = 11
_CRAWL_PRIORITY_NORMAL = 10
_CRAWL_PRIORITY_NEW = 6

_CRAWL_THRESHOLD = 60 * 60 * 2
_LEAF_CRAWL_DELAY = 60 * 60 * 24
_CATELOG_CRAWL_DELAY = 60 * 60 * 3

_UPDATE_CRAWL_THRESHOLD = 60 * 5

def get_last_crawl_limit():
    '''
    Only links with last crawl time less than threshold get crawled.
    '''
    now = get_epoch_datetime()
    return now - _CRAWL_THRESHOLD

def get_update_crawl_limit():
    '''
    Only links with last crawl time less than threshold get crawled.
    '''
    now = get_epoch_datetime()
    return now - _UPDATE_CRAWL_THRESHOLD

def get_priority_limit():
    '''
    Only links with priority higher or equal to normal get crawled. 
    '''
    return _CRAWL_PRIORITY_NORMAL


def prepare_link_item(item, curosr, when_insert):
    #Normalize url by removing trailing slash because there is no easy way to append slash
    item.url = item.url[:-1] if item.url[-1:] == '/' else item.url

    id = _assign_id(item.url)
    last_crawl = _assign_last_crawl(item.status, item.type, when_insert)
    priority = _assign_priority(id, item.status, when_insert)

    query_item = {
            'id' : id,
            'link' : item.url,
            'last_crawl' : last_crawl,
            'source' : item.source,
           }

    if item.pages:
        num = _get_pages(item.url, curosr, item.pages)
        if num:
            bonus = abs(float(num) / float(1000))
            priority = _assign_priority(id, item.status, when_insert, bonus)
            query_item['pages'] = item.pages
            print priority

    if priority:
        query_item['priority'] = priority

    return query_item


def _assign_priority(id, status, when_insert, bonus=None):
    priority = _CRAWL_PRIORITY_NORMAL

    if status == Status.FOUND and when_insert:
        priority = _CRAWL_PRIORITY_NEW
    elif status == Status.SUCCEED and bonus:
        priority = _CRAWL_PRIORITY_NORMAL - bonus
    elif status == Status.FAIL:
        priority = _CRAWL_PRIORITY_FAILED
    elif status == Status.REDIRECT:
        priority = _CRAWL_PRIORITY_MISSING
    elif status == Status.FOUND:
        priority = None
    return priority


def _assign_id(url):
    return get_str_md5(url)


def _assign_last_crawl(status, type, when_insert):
    if status == Status.FOUND:
        #Initialize last_crawl field value to 1 when the link is newly found, otherwise keep original value.
        return 1 if when_insert else None
    else:
        return get_epoch_datetime() + (_LEAF_CRAWL_DELAY if type == LinkType.LEAF else _CATELOG_CRAWL_DELAY)

def _get_pages(url, cursor, pages):
    sql = 'SELECT pages FROM new_link WHERE link = %s'
    cursor.execute(sql, url)
    result = cursor.fetchall()
    if result:
        return result[0][0] - pages
    return pages
