# coding=utf-8
import os
import MySQLdb
from hashlib import md5
import hashlib
import biplist
import ftplib
import httplib
import shutil
import time
import zipfile
import simplejson
from collections import namedtuple


class MySQLdbWrapper:

    conn = None

    def connect(self):
        self.conn = MySQLdb.connect('192.168.130.77', 'dev_market', 'market_dev_pwd', 'market')
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

api_host = '42.121.118.131:8080'
ftp_host = '42.121.118.131'
ftp_username = 'administrator'
ftp_password = '7cb1ea54'
ipa_file_dir = '/mnt/ctappstore100/vol158/ftphome/itunes'
root = '/mnt/ctappstore100/'
#ipa_file_dir = '/home/qpwang/nfs'
#root = '/home/qpwang/nfs/'
vol_id = ['158', '159', '17']


def start_download():
    while True:
        refresh_filename()
        sftp = ftplib.FTP(ftp_host, ftp_username, ftp_password)
        sftp.cwd('itunes\Mobile Applications')
        download_list = sftp.nlst()
        print download_list
        if not download_list:
            upload_conf()
            if refresh_conf():
                print "upload conf"
                time.sleep(300)
                continue
            else:
                print "upload conf error!"
                return
        for name in download_list:
            if name.endswith('.ipa'):
                print "start download: %s ,size: %d" % (name, sftp.size(name.decode('utf8')))
                ipa_path = '%s/%s' % (ipa_file_dir, name.decode('utf8'))
                sftp.retrbinary("RETR %s" % name, open(ipa_path, 'wb').write)
                sftp.delete("%s" % name.decode('utf8'))
                print "%s download finished!" % name.decode('utf8')
                analyzing_ipa(ipa_path, vol_id)
                print "%s import finished!" % name.decode('utf8')


def analyzing_ipa(file_path, vol_id):
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
    sig = 'ipa'
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
    apple_id = itunes['appleId']
    if '@' in apple_id:
        itunes['appleId'] = md5(itunes['appleId']).hexdigest().upper()
    ipainfo = {'appleId': itunes['appleId']}
    biplist.writePlist(ipainfo, 'ipainfo.plist')
    biplist.writePlist(itunes, 'iTunesMetadata.plist')
    root = biplist.readPlist(tmp_file)
    os.popen('sudo rm -r ./Payload')
    source = 'itunes.apple.com'
    app_id = itunes.get('itemId')
    source_link = get_source_link(app_id, apple_id)
    if not source_link:
        return
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
    print item.package_name, item.version_name
    package_hash = move_ipa(file_path, vol_id, download_link)
    insert_item(item, vol_id, download_link, source, sig, package_hash)
    return item


def get_source_link(app_id, apple_id):
    try:
        cursor = _db.cursor()
        sql = "select id,source_link from app_itunes where app_id = %s and apple_id = %s"
        cursor.execute(sql, (app_id, apple_id))
        result = cursor.fetchone()
        if result:
            id = result[0]
            sql = "update app_itunes set tag=1 where id=%s"
            cursor.execute(sql, id)
            _db.conn.commit()
            return result[1]
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()


def move_ipa(file_path, vol_id, download_link):
    vol_id = 'vol%s' % vol_id
    md = md5(download_link).hexdigest().upper()
    dir1 = md[:2]
    dir2 = md[2:4]
    name = '%s.%s' % (md, 'ipa')
    if not os.path.exists(os.path.join(root, vol_id, dir1, dir2)):
        os.makedirs(os.path.join(root, vol_id, dir1, dir2))
    path = os.path.join(root, vol_id, dir1, dir2, name)
    shutil.move(file_path, path)
    os.popen('zip -d "%s" iTunesMetadata.plist' % path)
    zf = zipfile.ZipFile(path, 'a')
    zf.write('iTunesMetadata.plist')
    zf.write('ipainfo.plist')
    command = 'md5sum %s' % path
    package_hash = os.popen(command).read()
    if not package_hash:
        package_hash = '-1'
    else:
        package_hash = package_hash.split()[0]
    return package_hash


def insert_item(item, vol_id, download_link, source, sig, package_hash):
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


def refresh_conf():
    conn = httplib.HTTPConnection(api_host)
    conn.request("GET", "/service/1/getconf")
    response = conn.getresponse()
    result = response.read()
    print result
    result = simplejson.loads(result)
    if not result['data']['result']:
        return True


def refresh_filename():
    conn = httplib.HTTPConnection(api_host)
    conn.request("GET", "/service/1/refreshfilename")
    response = conn.getresponse()
    result = response.read()
    print result


def upload_conf():
    file_path = 'itunes_apps.plist'
    download_list = get_download_list()
    get_conf_plist(download_list, file_path)
    sftp = ftplib.FTP(ftp_host, ftp_username, ftp_password)
    fp = open(file_path, 'rb')
    sftp.storbinary('STOR %s' % file_path, fp)
    fp.close()
    sftp.quit()


def get_conf_plist(download_list, file_path):
    biplist.writePlist(download_list, file_path, False)


def get_download_list():
    ipas = get_ipas()
    apple_id_dic = {}
    apps_dic = {}
    download_list = []
    for ipa in ipas:
        apple_id_dic[ipa[0]] = 0
        if ipa[0] in apps_dic:
            apps_dic[ipa[0]].append(ipa[1])
        else:
            apps_dic[ipa[0]] = [ipa[1]]
    apple_id_dic = get_account_info(apple_id_dic.keys())
    for key in apps_dic.keys():
        app = {'AppleId': key,
               'Password': apple_id_dic[key],
               'DownloadList': apps_dic[key]}
        download_list.append(app)
    return download_list


def get_account_info(apple_id):
    try:
        apple_id_dic = {}
        cursor = _db.cursor()
        sql = "SELECT username,password from apple_account where username in ('%s')" % "','".join(apple_id)
        cursor.execute(sql)
        results = cursor.fetchall()
        for result in results:
            apple_id_dic[result[0]] = result[1]
        return apple_id_dic
    except MySQLdb.Error as e:
        print e


def get_ipas():
    try:
        cursor = _db.cursor()
        sql = "SELECT apple_id, download_link, id FROM app_itunes WHERE tag is null and price = 0 limit 30"
        cursor.execute(sql)
        results = cursor.fetchall()
        id_set = [str(tup[2]) for tup in results]
        if id_set:
            sql = "UPDATE app_itunes set tag = 2 where id in (%s)" % ",".join(id_set)
            cursor.execute(sql)
            _db.conn.commit()
        return results
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()

if __name__ == "__main__":
    start_download()
