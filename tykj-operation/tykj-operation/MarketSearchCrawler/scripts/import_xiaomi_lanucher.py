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
        if i * 30 > 300:
            print 'finished'
            return 0
        apks = get_imgs(i * 30)
        report_status(apks)


def report_status(list):
    for l in list:
        try:
            cursor = _db.cursor()
            name = l.get('name')
            moduleId = l.get('moduleId')
            source = 'launcher.xiaomi.com'
            apk_size = l.get('fileSize')
            image_path = l.get('frontCover')
            base_url = l.get('downloadUrlRoot')
            icon_link = '%sjpeg/w270/%s' % (base_url, image_path)
            download_link = 'http://zhuti.xiaomi.com/download/%s' % moduleId
            source_link = 'http://market.xiaomi.com/thm/details/%s?&device=maguro&system=miui&version=4.0.4_330937' % moduleId
            downloads = l.get('downloads')
            category = '桌面主题'
            icon_path = _get_icon_path(icon_link)
            detail = get_detail(source_link)
            description = detail.get('description')
            publish_date = int(detail.get('modifyTime')) / 1000
            images_link = ' '.join(('%sjpeg/w965/%s' % (base_url, path)) for path in detail.get('snapshotsUrl'))
            images_path = ' '.join(_get_images_path(image_link) for image_link in images_link.split())
            version = detail.get('version')
            developer = detail.get('author')

            sql = "INSERT IGNORE INTO apt (name,source,apk_size," +\
                "icon_link,images,download_link,source_link," +\
                "downloads,version, category,icon_path,images_path, last_crawl,description,publish_date,developer) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, unix_timestamp(now()),%s ,%s ,%s)"
            cursor.execute(sql, (name, source, apk_size, icon_link, images_link, download_link, source_link,
                                 downloads, version, category, icon_path, images_path, description, publish_date, developer))
            _db.conn.commit()
        except MySQLdb.Error as e:
            print e
        finally:
            cursor.close()


def get_detail(source_link):
    conn = httplib.HTTPConnection('market.xiaomi.com')
    conn.request("GET", source_link)
    response = conn.getresponse()
    data = response.read()
    json = simplejson.loads(data)
    return json


def get_imgs(start):
    url = '/thm/subject/index?category=Launcher&&device=maguro&system=miui&version=4.0.4_330937&start=%s&count=30' % start
    conn = httplib.HTTPConnection('market.xiaomi.com')
    conn.request("GET", url)
    response = conn.getresponse()
    data = response.read()
    json = simplejson.loads(data).get('Launcher')
    print json
    return json


if __name__ == "__main__":
    start_refresh()
