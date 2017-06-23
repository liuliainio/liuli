# encoding=utf-8
import os
import time
import datetime
import shutil
import MySQLdb
import sys
import Image
import hashlib
import urllib
from cStringIO import StringIO
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.db import MySQLdbWrapper

_db = MySQLdbWrapper()

IMAGES_STORE = IMAGE_ROOT = '/mnt/ctappstore1/img/'


class DownloadImage():

    def process(self, url, source, dry_run=True):
        image_path = self._get_image_path(url, source)
        if not self._check_exist(image_path):
            meta = {}
            meta['source'] = source
            meta['path'] = image_path
            if not dry_run:
                self._create_request(url, meta)
            return image_path

    def _check_exist(self, path):
        image_path = '%s%s' % (IMAGES_STORE, path)
        return os.path.exists(image_path)

    def _create_request(self, link, meta):
        f = urllib.urlopen(link)
        data = f.read()
        self._parse(data, meta)

    def _on_error(self, fail):
        print str(fail)

    def _parse(self, data, meta):
        orig_image = Image.open(StringIO(data))
        conv_image, buff = self._convert_image(orig_image)
        path = meta['path']
        absolute_path = self._get_filesystem_path(path)
        self._mkdir(os.path.dirname(absolute_path))
        conv_image.save(absolute_path)

    def _convert_image(self, image, size=None):
        if image.format == 'PNG' and image.mode == 'RGBA':
            background = Image.new('RGBA', image.size, (255, 255, 255))
            background.paste(image, image)
            image = background.convert('RGB')
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        if size:
            image = image.copy()
            image.thumbnail(size, Image.ANTIALIAS)

        buf = StringIO()
        try:
            image.save(buf, 'JPEG')
        except Exception as ex:
            print "Cannot process image. Error: %s" % ex
        return image, buf

    def _get_filesystem_path(self, key):
        path_comps = key.split('/')
        return os.path.join(IMAGES_STORE, *path_comps)

    def _mkdir(self, dirname, domain=None):
        seen = self.created_directories[domain] if domain else set()
        if dirname not in seen:
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            seen.add(dirname)

    def _get_image_path(self, url, source):
        image_guid = hashlib.sha1(url).hexdigest()
        image_path = ''
        if source == 'icon':
            image_path = 'full/%s/%s/%s.jpg' % (image_guid[:1], image_guid[1:3], image_guid)
        elif source == 'image':
            image_path = 'full2/%s/%s/%s.jpg' % (image_guid[:1], image_guid[1:3], image_guid)
        else:
            print 'unidentified source %s' % source
        return image_path


def _get_file_hash(filepath):
    """Gets the MD5 hash of the file."""
    f = open(filepath, 'r')
    md5 = hashlib.md5()
    md5.update(f.read())
    return md5.hexdigest()

_IMAGE_DOWNLOADER = DownloadImage()


def start_refresh(dry_run=True, packages=None):
    end_date = int(time.time())
    start_date = end_date - 60 * 60 * 12
    source = ('as.baidu.com',)
    source_to = ('zhushou.360.cn', 'wandoujia.com')
    start_index, limit = 0, 100
    while True:
        final_apps = get_final_apps(
            start_date,
            end_date,
            source,
            start_index=start_index,
            limit=limit,
            packages=packages)
        if not final_apps:
            return
        for package_name, version_code, images_path, source_from in final_apps:
            if not images_path:
                print '[%s]NO IMAGES PATH in %s[%s,%s]' % (datetime.datetime.now(), source_from, package_name, version_code)
                continue
            try:
                old_images_path = []
                replace_images_path = []
                replace_images_url = []
                new_images_path = []
                for s in source_to:
                    match_app = get_app(package_name, version_code, s)
                    if not match_app:
                        print '[%s]NO MATCH APP in %s[%s,%s]' % (datetime.datetime.now(), s, package_name, version_code)
                        continue
                    print '[%s]MATCH APP in %s[%s,%s]' % (datetime.datetime.now(), s, package_name, version_code)
                    old_images_path = images_path.split()
                    replace_images_path = match_app[0].split() if match_app[0] else []
                    replace_images_url = match_app[1].split() if match_app[1] else []
                    new_images_path = []
                    if not replace_images_path:
                        print '[%s]MATCH APP NO IMAGES in %s[%s,%s]' % (datetime.datetime.now(), s, package_name, version_code)
                        continue
                    break

                if not replace_images_path or not old_images_path:
                    continue

                for url in replace_images_url:
                    local_path = _IMAGE_DOWNLOADER.process(url, 'image', dry_run=dry_run)
                    if local_path:
                        print '[%s]IMAGE DOWNLOADED %s-->%s' % (datetime.datetime.now(), url, local_path)
                # we just only replace the file instead of updating db use new
                # filepath.
                replaced = 0
                for img in replace_images_path:
                    if old_images_path:
                        replace_path = os.path.join(IMAGE_ROOT, img)
                        if not os.path.exists(replace_path):
                            print '[%s]IMAGE DOES NOT EXIST %s' % (datetime.datetime.now(), replace_path)
                            continue
                        old_img = old_images_path.pop(0)
                        old_path = os.path.join(IMAGE_ROOT, old_img)
                        if not dry_run:
                            if _get_file_hash(replace_path) == _get_file_hash(old_path):
                                print '[%s]IMAGE REPLACED %s, %s' % (datetime.datetime.now(), old_path, replace_path)
                                replaced += 1
                            else:
                                shutil.copyfile(replace_path, old_path)
                                print '[%s]REPLACE IMAGE %s, %s' % (datetime.datetime.now(), old_path, replace_path)
                        else:
                            print '[%s]REPLACE IMAGE %s, %s' % (datetime.datetime.now(), old_path, replace_path)
                        new_images_path.append(old_path)
                # if new_images_path > 0 but we still have old_images_path have
                # not  replaced, there are duplicated images maybe,
                # so we have to update db to reset image_path value.
                if new_images_path and old_images_path:
                    if replaced == len(new_images_path):
                        print '[%s]APP UPDATED %s[%s,%s]' % (datetime.datetime.now(), source_from, package_name, version_code)
                    else:
                        if not dry_run:
                            update_final_app(package_name, version_code, source_from, ' '.join(new_images_path))
                        print '[%s]UPDATE APP %s[%s,%s]' % (datetime.datetime.now(), source_from, package_name, version_code)
            except Exception as e:
                print '[%s]PROCESS FAILED [%s,%s]%s' % (datetime.datetime.now(), package_name, version_code, e)
        if packages:
            break
        start_index = start_index + limit
        print '[%s]PROCESSED %s %s' % (datetime.datetime.now(), start_date, start_index)


def get_final_apps(start_date, end_date, source, start_index=0, limit=100, packages=None):
    cursor = _db.cursor()
    try:
        if packages:
            where = " or ".join(["(package_name='%s' and version_code='%s')" % tuple(p.split(':')) for p in packages])
            sql = "SELECT package_name, version_code, images_path, source from final_app where %s" % where

        else:
            sql = "SELECT package_name, version_code, images_path, source from final_app where last_crawl >= %d and last_crawl <%d and source in (%s)  limit %d offset %d" \
                % (start_date, end_date, ','.join(["'%s'" % s for s in source]), limit, start_index)
        cursor.execute(sql)
        results = cursor.fetchall()
        return results
    except MySQLdb.Error as e:
        print '[%s]GET FINAL APPS FAILED %s' % (datetime.datetime.now(), e)
    finally:
        cursor.close()


def update_final_app(package_name, version_code, source, images_path):
    cursor = _db.cursor()
    try:
        sql = "UPDATE final_app set images_path='%s' where package_name='%s' and version_code='%s' and source='%s';" \
            % (images_path, package_name, version_code, source)
        cursor.execute(sql)
        _db.conn.commit()
    except MySQLdb.Error as e:
        print '[%s]UPDATE FINAL APP FAILED %s' % (datetime.datetime.now(), e)
    finally:
        cursor.close()


def get_app(package_name, version_code, source):
    cursor = _db.cursor()
    try:
        sql = "SELECT a.images_path, a.images from app a, duplicate_apk b where b.source='%s' and b.package_name='%s' and b.version_code='%s' and a.source_link = b.source_link; " \
            % (source, package_name, version_code)
        cursor.execute(sql)
        result = cursor.fetchone()
        return result
    except MySQLdb.Error as e:
        print '[%s]GET APP FAILED %s' % (datetime.datetime.now(), e)
    finally:
        cursor.close()


if __name__ == "__main__":
    dry_run = True
    packages = None
    if len(sys.argv) > 2:
        packages = sys.argv[2].split(',')
    if len(sys.argv) > 1:
        dry_run = {'True': True, 'False': False}.get(sys.argv[1], True)
    start_refresh(dry_run=dry_run, packages=packages)

