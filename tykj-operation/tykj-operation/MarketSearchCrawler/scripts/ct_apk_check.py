# coding=utf-8
import os
import MySQLdb


class MySQLdbWrapper:

    conn = None

    def connect(self):
        self.conn = MySQLdb.connect('localhost', 'root', 'P@55word', 'market_new')
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


def is_file_exist(file_path):

    pass


def init_file(file):
    dic = {'app_id': file[0],
           'app_size': file[1],
           'app_path': file[2],
           'package_name': file[3],
           'version_code': file[4],
           'version': file[5],
           'sig': file[6],
           'android_version': file[7],
           'adapter_screen': file[8],
           'app_type': file[9],
           'app_name': file[10],
           'app_cate': file[11],
           'app_desc': file[14],
           'developer': file[15],
           'rating': file[20],
           'publish_date': file[21],
           'rating_count': file[22],
           'downloads': file[23],
           }
    return dic


def check():
    while True:
        files = get_apk(100)
        if not files:
            return
        result_list = []
        report_list = []
        for file in files:
            file = init_file(file)
            result = check_file(file)
            if not result:
                report_list.append((file['app_id'], 2))
                continue
            result_list.append(result)
            report_list.append((file['app_id'], 1))
        insert_apk(result_list)
        report_status(report_list)


def check_apk():
    while True:
        apks = get_apk_files(500)
        if not apks:
            return
        report_list = []
        for apk in apks:
            path = '/media/20987cf3-4413-47df-a4a5-18d9cf006ce6/%s' % apk[1]
            if os.path.isfile(path):
                report_list.append((apk[0], 1))
            else:
                report_list.append((apk[0], 2))
        report_apk_status(report_list)


def check_file(file):
    if not file['package_name'] or not file['sig']:
        return None
#        file['package_name'],file['version_code'],file['version'] = get_package_info(file['app_path'])
#       if not file['package_name']:
 #          return None
    return file


def get_package_info(path):
    path = '/media/20987cf3-4413-47df-a4a5-18d9cf006ce6/%s' % path
    command_str = '../aapt d badging %s | grep package: | cut -d \\\' -f2,4,6' % path
    result = os.popen(command_str).read().strip()
    if not result:
        return None, None, None
    return result[0], result[1], result[2]


def get_apk(num):
    try:
        cursor = _db.cursor()
        sql = "SELECT distinct t_appinfo.APP_ID,FILE_SIZE,FILE_URL,PACKAGE_TITLE,PACKAGE_VERSION,VERSION_NAME,SIG,ANDROID_VERSION,ADAPTER_SCREEN,t_appinfo.APP_TYPE,APP_NAME,CATE_ID,FIRSTCATE_ID,SECONDCATE_ID,APP_BRIEF,AUTHOR,AVG_GRADE,TWOCODEBIGPIC,TWOCODESMALLPIC,TWOCODEID,REALAVG_GRADE,FIRST_ONSALE_DATE,GRADE_COUNT,DOWNLOAD_COUNT FROM t_uploadfile,t_apppackageinfo,t_appinfo where t_uploadfile.ITEM_ID = t_apppackageinfo.PACKAGE_ID and t_apppackageinfo.APP_ID = t_appinfo.APP_ID and FILE_EXT = 'apk' and t_appinfo.tag is  null  limit %d" % num
        cursor.execute(sql)
        result = cursor.fetchall()
        return result
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()


def get_apk_files(num):
    try:
        cursor = _db.cursor()
        sql = "SELECT id,file_path from app where tag is null limit %d " % num
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
            sql = "INSERT IGNORE INTO app (id,name,source,source_link,rating,version,developer,sdk_support,category,screen_support,apk_size,publish_date,downloads,description,last_crawl,package_name,version_code,file_path,vol_id, sig) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, unix_timestamp(%s), %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(
                sql,
                (file['app_id'],
                 file['app_name'],
                    'ctmarket',
                    file['app_path'],
                    file['rating'],
                    file['version'],
                    file['developer'],
                    file['android_version'],
                    file['app_cate'],
                    file['adapter_screen'],
                    file['app_size'],
                    file['publish_date'],
                    file['downloads'],
                    file['app_desc'],
                    1,
                    file['package_name'],
                    file['version_code'],
                    file['app_path'],
                    '1',
                    file['sig']))
        except MySQLdb.Error as e:
            print e
        finally:
            cursor.close()


def report_status(list):
    for l in list:
        try:
            cursor = _db.cursor()
            sql = "UPDATE t_appinfo SET tag = %s WHERE APP_ID = %s"
            cursor.execute(sql, (l[1], l[0]))
        except MySQLdb.Error as e:
            print e
        finally:
            cursor.close()


def report_apk_status(list):
    for l in list:
        try:
            cursor = _db.cursor()
            sql = 'update app set tag = %s where id = %s'
            cursor.execute(sql, (l[1], l[0]))
        except MySQLdb.Error as e:
            print e
        finally:
            cursor.close()


if __name__ == "__main__":
#    check()
    check_apk()
