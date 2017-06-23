'''
Created on Dec 17, 2012

@author: yyu

This file is temporarily used to batch update min_sdk_version field in unique_apk tables.
It's not required in any production environment.

It takes time to run, so execute this with following command:
    nohup python -m MarketSearch.apkfilter_batch > result.txt

'''
import os
import MySQLdb
from apkfilter import Apkfilter
from MarketSearch.file import get_path
from MarketSearch.db import MySQLdbWrapper
from MarketSearch.itemfilter import MIN_SDK_VERSION_NOT_APPLIED


def process():
    try:
        _db = MySQLdbWrapper()
        cursor = _db.cursor()
        sql = 'SELECT vol_id, download_link, source, id FROM unique_apk where min_sdk_version IS NULL'
        cursor.execute(sql)
        items = cursor.fetchall()

        for item in items:
            vol_id = item[0]
            key_url = item[1]
            source = item[2]
            pk = item[3]

            apk_info = None
            if source in ['appchina.com', 'goapk.com', 'nduoa.com', 'mumayi.com', 'hiapk.com']:
                f = Apkfilter()
                if vol_id in ['2', '3', '4', '5', '11', '12']:
                    root_path = '/mnt/ctappstore1/'
                else:
                    root_path = '/mnt/ctappstore2/'

                file_path = get_path(vol_id, key_url, 'apk', root=root_path, mkdir=False)
                if not os.path.exists(file_path):
                    continue

                apk_info = f._filter(file_path)
                _update_min_sdk_version(pk, apk_info)
            else:
                # Update min_sdk_version no matter we can extract apk info or not.
                _update_min_sdk_version(pk)
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()


def _update_min_sdk_version(pk, apk_info=None):
    try:
        _db = MySQLdbWrapper()
        cursor = _db.cursor()
        sql = 'UPDATE unique_apk SET min_sdk_version = %s where id = %s'
        cursor.execute(sql, (MIN_SDK_VERSION_NOT_APPLIED if not apk_info else apk_info.min_sdk_version, pk))
        cursor.connection.commit()
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()


if __name__ == "__main__":
    process()
