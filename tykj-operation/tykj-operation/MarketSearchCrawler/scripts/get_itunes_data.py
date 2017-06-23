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

path = './ftphome'
ItemInfo = namedtuple(
    'ItemInfo',
    ['package_name',
     'version_code',
     'min_sdk_version',
     'version_name',
     'apk_size',
     'screen_support',
     'is_break',
     'file_type',
     'platform'])


def get_ipas(path):
    file_list = []
    for d in os.listdir(path):
        if os.path.isdir(os.path.join(path, d)):
            for f in os.listdir(os.path.join(path, d)):
                if f.endswith('.ipa'):
                    file_list.append(os.path.join(path, d, f))
    return file_list


def get_item(file_path):
    sig = 'ipa'
    if '\xe6\xb8\xb8\xe6\x88\x8f' in file_path.split('/')[-2]:
        if '-' in file_path.split('/')[-2]:
            sig = file_path.split('/')[-2].split('-')[1]
            if sig in ['\xe4\xbd\x93\xe8\x82\xb2', '\xe9\x9f\xb3\xe4\xb9\x90']:
                sig = sig + '\xe6\xb8\xb8\xe6\x88\x8f'
        else:
            sig = file_path.split('/')[-2]
        print sig
    zf = zipfile.ZipFile(file_path)
    is_break = 1
    for f in zf.namelist():
        if f.endswith('.app/Info.plist'):
            tmp_file = f
            zf.extract(f)
        elif '.app/SC_Info' in f:
            is_break = 0
    zf.extract('iTunesMetadata.plist')
    itunes = biplist.readPlist('iTunesMetadata.plist')
    itunes['appleId'] = md5(itunes['appleId']).hexdigest().upper()
    biplist.writePlist(itunes, 'iTunesMetadata.plist')
    root = biplist.readPlist(tmp_file)
    os.popen('sudo rm -r Payload')
    source = 'itunes.apple.com'
    app_id = itunes.get('itemId')
    source_link = 'https://itunes.apple.com/cn/app/id%s?mt=8' % app_id
    vol_id = '159'
    download_link = source_link
    app_name = itunes.get('itemName')
    apk_size = os.stat(file_path).st_size
    min_sdk_version = (root.get('MinimumOSVersion').replace('.', '') + '0000')[:4]
    file_type = 'ipa'
    package_name = root.get('CFBundleIdentifier')
    screen_support = 0
#    print itunes
    for i in root.get('UIDeviceFamily'):
        screen_support += int(i)
    if screen_support == 1:
        platform = 4
    elif screen_support == 2:
        platform = 8
    elif screen_support == 3:
        platform = 12
    if isinstance(root.get('CFBundleVersion'), str) and '.' in root.get('CFBundleVersion') and root.get('CFBundleVersion').replace('.', '').isdigit():
        version_name = root.get('CFBundleVersion')
    elif isinstance(root.get('CFBundleShortVersionString'), str) and root.get('CFBundleShortVersionString').replace('.', '').isdigit():
        version_name = root.get('CFBundleShortVersionString')
    else:
        version_name = root.get('CFBundleVersion')
    i = 0
    version_code = 0
    if '.' not in version_name:
        version_code = int(version_name)
    else:
        for v in version_name.split('.'):
            if i == 0:
                v = v[:5]
                version_code += int(v) << 50
            elif i < 4:
                v = v[:4]
                version_code += int(v) << 50 - i * 12
            elif i == 4:
                v = v[:5]
                version_code += int(v)
            if i > 4:
                break
            i += 1
    # print source_link,app_id
    item = ItemInfo(package_name=package_name,
                    version_code=int(version_code) if version_code else 0,
                    version_name=version_name,
                    apk_size=str(apk_size),
                    min_sdk_version=int(min_sdk_version) if min_sdk_version else 0,
                    screen_support=str(screen_support),
                    is_break=is_break,
                    file_type=file_type,
                    platform=platform)
    # print item
    insert_link(source_link, source)
    move_ipa(file_path, vol_id, download_link)
    insert_item(item, vol_id, download_link, source, sig)
    return item


def insert_item(item, vol_id, download_link, source, sig='ipa'):
    try:
        cursor = _db.cursor()
        sql = 'INSERT IGNORE INTO unique_apk (package_name, version_code, source_link, download_link, source, vol_id, sig, version, apk_size, min_sdk_version, screen_support, is_break, file_type, platform) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(
            sql,
            (item.package_name,
             item.version_code,
             download_link,
             download_link,
             source,
             vol_id,
             sig,
             item.version_name,
             item.apk_size,
             item.min_sdk_version,
             item.screen_support,
             item.is_break,
             item.file_type,
             item.platform))
        _db.conn.commit()
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()


def move_ipa(file_path, vol_id, download_link):
    root = '/mnt/ctappstore100/'
    vol_id = 'vol%s' % vol_id
    md = md5(download_link).hexdigest().upper()
    dir1 = md[:2]
    dir2 = md[2:4]
    name = '%s.%s' % (md, 'ipa')
    if not os.path.exists(os.path.join(root, vol_id, dir1, dir2)):
        os.makedirs(os.path.join(root, vol_id, dir1, dir2))
    path = os.path.join(root, vol_id, dir1, dir2, name)
    shutil.copy(file_path, path)
    os.popen('zip -d %s iTunesMetadata.plist' % path)
    zf = zipfile.ZipFile(path, 'a')
    zf.write('iTunesMetadata.plist')
    print file_path, path


def insert_link(source_link, source):
    try:
        cursor = _db.cursor()
        sql = "insert ignore into new_link (id, source, link, last_crawl, priority) values ('%s', '%s', '%s', 1, 10);" % (
            md5(source_link).hexdigest().upper(),
            source,
            source_link)
        cursor.execute(sql)
        _db.conn.commit()
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()


def start_insert():
    files = get_ipas(path)
    print len(files)
    if not files:
        return
    i = 0
    for ipa_file in files:
        i += 1
        try:
            ipa_item = get_item(ipa_file)
            print i
        except Exception as e:
            print e

if __name__ == "__main__":
    start_insert()
