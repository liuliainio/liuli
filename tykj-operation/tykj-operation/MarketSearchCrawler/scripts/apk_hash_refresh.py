# encoding=utf-8
import os
import MySQLdb
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.db import MySQLdbWrapper

_db = MySQLdbWrapper()

VOL_MAPPING = {
    'vol3': '/mnt/ctappstore1',
    'vol4': '/mnt/ctappstore1',
    'vol5': '/mnt/ctappstore1',
    'vol11': '/mnt/ctappstore1',
    'vol12': '/mnt/ctappstore1',

    'vol1': '/mnt/ctappstore2',
    'vol6': '/mnt/ctappstore2',
    'vol7': '/mnt/ctappstore2',
    'vol8': '/mnt/ctappstore2',
    'vol10': '/mnt/ctappstore2',

    'vol9': '/mnt/ctappstore3',
    'vol13': '/mnt/ctappstore3',
    'vol14': '/mnt/ctappstore3',

    'vol2': '/mnt/ctappstore4',
    'vol15': '/mnt/ctappstore4',
    'vol16': '/mnt/ctappstore4',
    'vol17': '/mnt/ctappstore4',

    'vol18': '/mnt/ctappstore5',
    'vol19': '/mnt/ctappstore5',

    'vol155': '/mnt/ctappstore100',
    'vol156': '/mnt/ctappstore100',
    'vol157': '/mnt/ctappstore100',
    'vol158': '/mnt/ctappstore100',
    'vol159': '/mnt/ctappstore100',
    'vol161': '/mnt/ctappstore100',
    'vol162': '/mnt/ctappstore100',
    'vol163': '/mnt/ctappstore100',
    'vol164': '/mnt/ctappstore100',
    'vol107': '/mnt/ctappstore100',

    'vol343': '/mnt/ctappstore300',
    'vol344': '/mnt/ctappstore300',
    'vol345': '/mnt/ctappstore300',
    'vol346': '/mnt/ctappstore300',
    'vol349': '/mnt/ctappstore300',
    'vol350': '/mnt/ctappstore300',
    'vol351': '/mnt/ctappstore300',
    'vol352': '/mnt/ctappstore300',
    'vol353': '/mnt/ctappstore300',
    'vol354': '/mnt/ctappstore300',
}


def start_refresh():
    while True:
        apks = get_apks()
        if not apks:
            return
        print len(apks)
        for id, vol_id, file_path, hash_old in apks:
            try:
                root_path = VOL_MAPPING.get('vol%s' % vol_id, None)
                if not root_path:
                    #report_status(id, -1)
                    print 'NO ROOT_PATH %s,%s' % (id, vol_id)
                else:
                    full_path = '%s/vol%s/%s' % (root_path, vol_id, file_path)
                    if not os.path.exists(full_path):
                        print 'FULL_PATH doesnot exists %s,%s' % (id, full_path)
                    else:
                        command = 'md5sum %s' % full_path
                        package_hash = os.popen(command).read().split()[0]
                        if hash_old != package_hash:
                            report_status(id, package_hash)
                            print 'SUCCESS %s,%s,%s,%s' % (id, hash_old, package_hash, full_path)
            except Exception as e:
                print e
                #report_status(id, -1)
        break


def report_status(id, package_hash):
    cursor = _db.cursor()
    try:
        sql = "UPDATE final_app set package_hash='%s' where id = %s" % (package_hash, id)
        cursor.execute(sql)
        cursor.connection.commit()
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()


def get_apks():
    cursor = _db.cursor()
    try:
        #!!!!sql = "SELECT id, vol_id, file_path from final_app where package_hash is NULL limit 100;"
        sql = "SELECT id, vol_id, file_path, package_hash from final_app where source='myapp.com';"
        cursor.execute(sql)
        results = cursor.fetchall()
        return results
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()


if __name__ == "__main__":
    start_refresh()

