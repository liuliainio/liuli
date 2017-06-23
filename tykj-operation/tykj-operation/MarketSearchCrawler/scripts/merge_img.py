# coding=utf-8
import os
import MySQLdb
from hashlib import md5
from BeautifulSoup import BeautifulSoup
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.db import MySQLdbWrapper

_db = MySQLdbWrapper()


def init_file(file):
    dic = {'id': file[0],
           'name': file[1],
           'icon_link': file[2],
           'icon_path': file[3],
           'source': file[4],
           'source_link': file[5],
           'rating': file[6],
           'version': file[7],
           'developer': file[8],
           'sdk_support': file[9],
           'category': file[10],
           #           'screen_support':file[11],
           'screen_support': None,
           'apk_size': file[12],
           'language': file[13],
           'publish_date': file[14],
           'downloads': file[15],
           'description': file[16],
           'images': file[17],
           'images_path': file[18],
           'qr_link': file[19],
           'download_link': file[20],
           'last_crawl': file[21],
           'vol_id': '11',
           'package_name': file[3].split('/')[-1].split('.')[0],
           'version_code': 1,
           'sig': 'img',
           'min_sdk_version': -1,
           }
    return dic


def merge():
    while True:
        files = get_apk(1)
        if not files:
#            update_final_app_version()
            return
        result_list = []
        report_list = []
        for file in files:
            file = init_file(file)
            result_list.append(file)
            report_list.append((file['id'], 10))
        insert_apk(result_list)
        report_status(report_list)


def update_final_app_version():
    try:
        cursor = _db.cursor()
        sql = '''
        insert ignore into final_app_version
            (id,package_name,version_code,img_status)
        select a.id,b.package_name,b.version_code,\'11\'
        from final_app a
            join(select package_name ,MAX(version_code ) as version_code
                from final_app Group by package_name)b
            on a.source=\'image.91.com\' a.package_name=b.package_name
                and a.version_code=b.version_code
        '''
        cursor.execute(sql)
        _db.conn.commit()
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()


def get_apk(num):
    try:
        cursor = _db.cursor()
        sql = """
        SELECT id,name,icon_link,icon_path,source,source_link,rating,version,
            developer,sdk_support,category,screen_support,apk_size,language,
            publish_date,downloads,description,images,images_path,qr_link,
            download_link,last_crawl
        FROM img
        WHERE tag = 1 limit %d
        """ % num
        cursor.execute(sql)
        result = cursor.fetchall()
        return result
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()


def insert_apk(list):
    for file in list:
        try:
            cursor = _db.cursor()
            sql = """
            INSERT IGNORE INTO final_app
                (name,icon_link,icon_path,source,source_link,rating,version,
                developer,sdk_support,category,screen_support,apk_size,
                language,publish_date,downloads,description,images,images_path,
                qr_link,download_link,last_crawl,package_name,version_code,
                file_path,vol_id, sig, min_sdk_version)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (file['name'], file['icon_link'], file['icon_path'],
                                 file['source'], file['source_link'], file['rating'],
                                 file['version'], file['developer'], file['sdk_support'],
                                 file['category'], file['screen_support'], file['apk_size'],
                                 file['language'], file['publish_date'], file['downloads'],
                                 file['description'], file['images'], file['images_path'],
                                 file['qr_link'], file['download_link'], file['last_crawl'],
                                 file['package_name'], file['version_code'],
                                 '/'.join(file['images_path'].split('/')[1:]),
                                 file['vol_id'], file['sig'], file['min_sdk_version']))
            _db.conn.commit()
        except MySQLdb.Error as e:
            print e
        finally:
            cursor.close()


def report_status(list):
    for l in list:
        try:
            cursor = _db.cursor()
            sql = "UPDATE img SET tag = %s WHERE id = %s"
            cursor.execute(sql, (l[1], l[0]))
            _db.conn.commit()
        except MySQLdb.Error as e:
            print e
        finally:
            cursor.close()

if __name__ == "__main__":
    merge()
