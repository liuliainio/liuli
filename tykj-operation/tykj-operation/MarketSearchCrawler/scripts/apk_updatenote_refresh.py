# encoding=utf-8
import time
import datetime
import MySQLdb
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.db import MySQLdbWrapper

_db = MySQLdbWrapper()


def start_refresh(dry_run=True, packages=None):
    end_date = int(time.time())
    start_date = end_date - 60 * 60 * 12 * 2 * 7
    source = ('as.baidu.com', 'zhushou.360.cn', 'wandoujia.com', 'appchina.com')
    source_to = ('myapp.com', 'hiapk.com')
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
        for package_name, version_code, source_from in final_apps:
            try:
                update_note = ""
                for s in source_to:
                    match_app = get_app(package_name, version_code, s)
                    if not match_app:
                        print '[%s]NO MATCH APP in %s[%s,%s]' % (datetime.datetime.now(), s, package_name, version_code)
                        continue
                    print '[%s]MATCH APP in %s[%s,%s]' % (datetime.datetime.now(), s, package_name, version_code)
                    update_note = match_app[0]
                    if not update_note:
                        print '[%s]NO UPDATE NOTE in %s[%s,%s]' % (datetime.datetime.now(), s, package_name, version_code)
                        continue

                    if update_note:
                        update_final_app(package_name, version_code, source_from, update_note)
                        print '[%s]UPDATE APP %s[%s,%s]' % (datetime.datetime.now(), source_from, package_name, version_code)
                    else:
                        print '[%s]NO UPDATE NOT %s[%s,%s]' % (datetime.datetime.now(), source_from, package_name, version_code)
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
            sql = "SELECT package_name, version_code, source from final_app where %s" % where

        else:
            sql = "SELECT package_name, version_code, source from final_app where (update_note='' or update_note is NULL) and last_crawl >= %d and last_crawl <%d and source in (%s)  limit %d offset %d" \
                % (start_date, end_date, ','.join(["'%s'" % s for s in source]), limit, start_index)
        cursor.execute(sql)
        results = cursor.fetchall()
        return results
    except MySQLdb.Error as e:
        print '[%s]GET FINAL APPS FAILED %s' % (datetime.datetime.now(), e)
    finally:
        cursor.close()


def update_final_app(package_name, version_code, source, update_note):
    cursor = _db.cursor()
    try:
        sql = "UPDATE final_app set update_note='%s' where package_name='%s' and version_code='%s' and source='%s';" \
            % (update_note, package_name, version_code, source)
        cursor.execute(sql)
        _db.conn.commit()
    except MySQLdb.Error as e:
        print '[%s]UPDATE FINAL APP FAILED %s' % (datetime.datetime.now(), e)
    finally:
        cursor.close()


def get_app(package_name, version_code, source):
    cursor = _db.cursor()
    try:
        sql = "SELECT a.update_note from app a, duplicate_apk b where b.source='%s' and b.package_name='%s' and b.version_code='%s' and a.source_link = b.source_link; " \
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

