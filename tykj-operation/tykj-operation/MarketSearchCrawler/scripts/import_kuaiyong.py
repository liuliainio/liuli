# encoding=utf-8
import simplejson
import MySQLdb
import hashlib
import httplib
from datetime import datetime
from time import mktime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.db import MySQLdbWrapper

cate_app_list = [-1, 0, 54, 57, 59, 62, 64, 66, 69, 86, 80, 87, 78, 85, 76, 83, 88, 90, 81, 89, 91, 95, 84, 82]
cate_game_list = [-1, 0, 52, 53, 55, 65, 71, 68, 56, 70, 67, 73, 74, 75, 79, 58, 61, 63, 77, 60, 72]

_db = MySQLdbWrapper()


def _get_icon_path(icon_link):
        image_guid = hashlib.sha1(icon_link).hexdigest()
        return 'full/%s/%s/%s.jpg' % (image_guid[:1], image_guid[1:3], image_guid)


def _get_images_path(images):
    images_path = []
    for image in images.split():
        image_guid = hashlib.sha1(image).hexdigest()
        image_path = 'full2/%s/%s/%s.jpg' % (image_guid[:1], image_guid[1:3], image_guid)
        images_path.append(image_path)
    return ' '.join(images_path)


def _adapt_date_str(date_str):
    if not date_str:
        return None
    date = datetime.strptime(date_str, "%Y-%m-%d")
    return int(mktime(date.timetuple()))


def start_refresh():
    for cate in cate_app_list:
        for i in range(300):
            if i * 27 > 300:
                print 'cate: %s finished' % cate
                break
            apks = get_ipas(i * 27 + 1, cate)
            report_status(apks)


def report_status(list):
    if not list:
        return
    for l in list:
        try:
            cursor = _db.cursor()
            name = l.get('APPNAME')
            source = 'ipa.kuaiyong.com'
            apk_size = l.get('APPSIZE')
            icon_link = l.get('APPICONURL')
            download_link = l.get('URL')[0].get('url')
            source_link = download_link
            downloads = l.get('APPDOWNCOUNT')
            category = l.get('CATEGORY')
            icon_path = _get_icon_path(icon_link)
            detail = get_detail(source_link)
            description = detail.get('APPINFOR').get('APPDETAILINTRO')
            publish_date = _adapt_date_str(l.get('APPUPDATETIME'))
            images = ' '.join(detail.get('APPINFOR').get('APPPREVIEWURLS'))
            images_path = _get_images_path(images)
            version = l.get('APPVERSION')

            sql = "INSERT IGNORE INTO app_ios (name,source,apk_size," +\
                "icon_link,download_link,source_link," +\
                "downloads, category,icon_path,images, images_path, description, publish_date, version, last_crawl) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s ,%s, unix_timestamp(now()))"
            cursor.execute(sql, (name, source, apk_size, icon_link, download_link, source_link,
                                 downloads, category, icon_path, images, images_path, description, publish_date, version))
            _db.conn.commit()
        except MySQLdb.Error as e:
            print e
        finally:
            cursor.close()


def get_ipas(start, category):
    if category in cate_app_list:
        url = "/Interface/i_kysearch.php?client=1.5.0.6&page=newestapp&device=all&categoryid=%s&version=0&begin=%s&end=%s" % (
            category,
            start,
            start + 27)
    else:
        url = "/Interface/i_kysearch.php?client=1.5.0.6&page=newestgame&device=all&categoryid=%s&version=0&begin=%s&end=%s" % (
            category,
            start,
            start + 27)
    try:
        conn = httplib.HTTPConnection('f_apps.bppstore.com')
        conn.request("GET", url)
        response = conn.getresponse()
        data = response.read()
        json = simplejson.loads(data.decode('utf-8-sig'))
        return json[1:]
    except Exception as e:
        print e


def get_detail(url):
    url = "http://appdown.wanmeiyueyu.com/Data/APPINFOR/30/90/com.ninjacatcn.ourgame/dizigui_zhouyi_com.ninjacatcn.ourgame_1353600000_1.1.4.ipa"
    url = '/'.join(url[30:].split('/')[:-1]) + '/ipadetailinfor_' + url.split('_')[-1][:-4]
    conn = httplib.HTTPConnection('pic.wanmeiyueyu.com')
    conn.request("GET", url)
    response = conn.getresponse()
    data = response.read()
    json = simplejson.loads(data[20:])
    return json

if __name__ == "__main__":
    start_refresh()
