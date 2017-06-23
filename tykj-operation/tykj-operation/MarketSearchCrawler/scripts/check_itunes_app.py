# coding=utf-8
import os
import sys
import biplist
import zipfile
import shutil
from collections import namedtuple
from hashlib import md5
import MySQLdb

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.db import MySQLdbWrapper

_db = MySQLdbWrapper()

hash_id_dic = {}
app_num_dic = {}


def hash_apple_id():
    try:
        cursor = _db.cursor()
        sql = "SELECT id,username from apple_account"
        cursor.execute(sql)
        results = cursor.fetchall()
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()
    for id, username in results:
        print id, username
        hash_id = md5(username).hexdigest().upper()
        hash_id_dic[hash_id] = username
        app_num_dic[username] = 0


def check_app():
    hash_apple_id()
    bad_id_dic = {}
    i = 0
    while True:
        ipas = get_ipas()
        if not ipas:
            update_app_num()
            print bad_id_dic.keys()
            return
        report_list = []
        for ipa in ipas:
            i += 1
            file_name = md5(ipa[2]).hexdigest().upper()
            path = '/mnt/ctappstore100/vol%s/%s/%s/%s.ipa' % (ipa[1], file_name[:2], file_name[2:4], file_name)
            zf = zipfile.ZipFile(path)
            zf.extract('iTunesMetadata.plist')
            itunes = biplist.readPlist('iTunesMetadata.plist')
            if itunes['appleId'] in hash_id_dic:
                app_num_dic[hash_id_dic[itunes['appleId']]] = app_num_dic[hash_id_dic[itunes['appleId']]] + 1
                report_list.append((ipa[3], hash_id_dic[itunes['appleId']]))
            else:
                print itunes['appleId']
                bad_id_dic[itunes['appleId']] = 1
            print i
        report_status(report_list)


def update_app_num():
    for username in app_num_dic.keys():
        try:
            cursor = _db.cursor()
            sql = "update apple_account set app_num=%d where username=%s"
            cursor.execute(sql, (app_num_dic[username], username))
            _db.conn.commit()
        except MySQLdb.Error as e:
            print e
        finally:
            cursor.close()


def report_status(list):
    for l in list:
        try:
            cursor = _db.cursor()
            sql = "update app_ios set screen_support=%s where source_link=%s and source='itunes.apple.com'"
            cursor.execute(sql, (l[1], l[0]))
            _db.conn.commit()
        except MySQLdb.Error as e:
            print e
        finally:
            cursor.close()


def get_ipas():
    try:
        cursor = _db.cursor()
        sql = "SELECT id,vol_id,download_link,source_link from unique_apk where source='itunes.apple.com' and tag is null limit 100"
        cursor.execute(sql)
        results = cursor.fetchall()
        sql = "update unique_apk set tag=1 where source='itunes.apple.com' and tag is null limit 100"
        cursor.execute(sql)
        _db.conn.commit()
        return results
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()


if __name__ == "__main__":
    hash_apple_id()
