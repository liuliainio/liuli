# encoding=utf-8
import os
import MySQLdb
import zipfile
import shutil
from hashlib import md5


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

img_root1 = '/mnt/ctappstore1/img/'
img_root2 = '/mnt/ctappstore2/vol1/'


def start_refresh():
    i = 0
    while True:
        apks = get_apks()
        if not apks:
            print "finished"
            return
        report_list = []
        for apk in apks:
            i += 1
            vol_id = apk[0]
            file_path = apk[1]
            icon_path = apk[2]
            if not icon_path:
                icon_path = 'data/app_files/2010/11/%s.png' % md5(file_path).hexdigest()
                print icon_path
            id = apk[3]
            path = get_path(vol_id, file_path)
            icon_path = get_icon(path, icon_path)
            report_list.append((icon_path, id))
            print i, icon_path, id
        report_status(report_list)
        return


def get_icon(path, icon_path):
    try:
        command_str = './aapt d badging %s |grep "application: label"' % path
        result = os.popen(command_str).read().strip()
        icon_file = result.split('icon=')[1].replace("'", '')
        print icon_file, path
        zf = zipfile.ZipFile(path)
        icon_path = icon_path.split('.')[0] + '.' + icon_file.split('.')[1]
        if icon_path.startswith('data'):
            img_root = img_root2
        else:
            img_root = img_root1
        zf.extract(icon_file)
        print 'done'
        shutil.move(icon_file, img_root + icon_path)
        shutil.rmtree(icon_file.split('/')[0])
        return icon_path
    except Exception as e:
        print e


def get_path(vol_id, file_path):
    if int(vol_id) in [3, 4, 5, 11, 12]:
        return '/mnt/ctappstore1/vol%s/%s' % (vol_id, file_path)
    elif int(vol_id) in [1, 6, 7, 8, 10]:
        return '/mnt/ctappstore2/vol%s/%s' % (vol_id, file_path)
    elif int(vol_id) in [9, 13, 14]:
        return '/mnt/ctappstore3/vol%s/%s' % (vol_id, file_path)
    elif int(vol_id) in [2, 15, 16, 17]:
        return '/mnt/ctappstore4/vol%s/%s' % (vol_id, file_path)
    elif int(vol_id) in [107, 155, 156, 157, 158, 159]:
        return '/mnt/ctappstore100/vol%s/%s' % (vol_id, file_path)
    elif int(vol_id) in [343, 344, 345, 346, 349, 350, 351, 352, 353, 354]:
        return '/mnt/ctappstore300/vol%s/%s' % (vol_id, file_path)


def report_status(list):
    for l in list:
        try:
            cursor = _db.cursor()
            sql = "UPDATE final_app set is_refresh=21,icon_path=%s where id = %s"
            cursor.execute(sql, (l[0], l[1]))
            _db.conn.commit()
        except MySQLdb.Error as e:
            print e
        finally:
            cursor.close()


def get_apks():
    try:
        cursor = _db.cursor()
        sql = "SELECT vol_id,file_path,icon_path,id from final_app where file_type='apk' and (is_refresh not in (22,21) or is_refresh is null) limit 100"
#        sql = "SELECT vol_id,file_path,icon_path,id from final_app where id=50652"
        cursor.execute(sql)
        results = cursor.fetchall()
        id_set = [str(tup[3]) for tup in results]
        sql = "UPDATE final_app set is_refresh = 22 where id in (%s)" % ','.join(id_set)
        cursor.execute(sql)
        _db.conn.commit()
        return results
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()

if __name__ == "__main__":
    start_refresh()
