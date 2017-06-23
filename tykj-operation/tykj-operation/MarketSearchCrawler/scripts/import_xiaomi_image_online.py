# encoding=utf-8
import os
import sys
import simplejson
import MySQLdb
import hashlib
from xml.etree.ElementTree import fromstring
from hashlib import md5
import httplib
import urllib

FS_ROOT = '/home/qpwang/nfs'


class MySQLdbWrapper:

    conn = None

    def connect(self):
        self.conn = MySQLdb.connect('localhost', 'root', 'P@55word', 'market')
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


def get_str_md5(str=None):
    return md5(str).hexdigest().upper()


def get_path(vol_id, key_url, suffix):
    vol_id = 'vol%s' % vol_id
    md5 = get_str_md5(key_url)
    dir1 = md5[:2]
    dir2 = md5[2:4]
    name = '%s.%s' % (md5, suffix)
    if not os.path.exists(os.path.join(FS_ROOT, vol_id, dir1, dir2)):
        os.makedirs(os.path.join(FS_ROOT, vol_id, dir1, dir2))
    return os.path.join(FS_ROOT, vol_id, dir1, dir2, name)


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


def start_refresh():
    for i in range(300):
        if i * 30 > 8550:
            print 'finished'
            return 0
        apks = get_imgs(i * 30)
        report_status(apks)


def report_status(list):
    for l in list:
        try:
            cursor = _db.cursor()
            name = l.get('name')
            source = 'lock.image.xiaomi.com'
            apk_size = l.get('fileSize')
            image_path = l.get('frontCover')
            base_url = l.get('downloadUrlRoot')
            icon_link = '%sjpeg/w270/%s' % (base_url, image_path)
            images_link = '%sjpeg/w540/%s' % (base_url, image_path)
            download_link = images_link
            source_link = images_link
            downloads = l.get('downloads')
            version = 1
            category = '锁屏壁纸'
            icon_path = _get_icon_path(icon_link)
            images_path = _get_images_path(images_link)

            sql = "INSERT IGNORE INTO img (name,source,apk_size," +\
                "icon_link,images,download_link,source_link," +\
                "downloads,version, category,icon_path,images_path, last_crawl,tag) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, unix_timestamp(now()), 10)"
            cursor.execute(sql, (name, source, apk_size, icon_link, images_link, download_link, source_link,
                                 downloads, version, category, icon_path, images_path))
            _db.conn.commit()
        except MySQLdb.Error as e:
            print e
        finally:
            cursor.close()


def get_imgs(start):
    url = '/thm/subject/index?category=LockScreenWallpaper&device=maguro&system=miui&version=4.0.4_330937&start=%s&count=30' % start
    conn = httplib.HTTPConnection('market.xiaomi.com')
    conn.request("GET", url)
    response = conn.getresponse()
    data = response.read()
    json = simplejson.loads(data).get('WallpaperUnion')
    print json
    return json


def update():
    cursor = _db.cursor()
    sql = "update img set category='桌面壁纸' where source='image.xiaomi.com'"
    cursor.execute(sql)
    _db.conn.commit()

if __name__ == "__main__":
#    start_refresh()
    update()
