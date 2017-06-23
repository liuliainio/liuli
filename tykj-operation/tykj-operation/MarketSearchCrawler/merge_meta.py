#-*- coding: utf-8 -*-
'''
Created on Aug 23, 2013

@author: gmliao
'''
import MySQLdb
from services.db import MySQLdbWrapper


_db = MySQLdbWrapper()


max_id = 2407300
stop_id = 0
count = 50
debug = False


def get_final_app(id_from, id_to, count):
    try:
        c = _db.cursor()
        sql = '''
        select id, source_link, package_name, version_code,
            avail_download_links, update_note, labels
        from final_app
        where id < %s and id >= %s and file_type='apk'
            order by id desc
            limit %s
        ''' % (id_from, id_to, count)
        if debug:
            print sql.encode('utf-8')
        c.execute(sql)
        result = c.fetchall()
        return result
    finally:
        c.close()


def get_update_info(source_link, package_name, version_code,
                    avail_download_links, update_note, labels):
    try:
        c = _db.cursor()
        sql = '''
        select app.download_link, app.update_note, app.labels
        from duplicate_apk da
            join app on app.source_link = da.source_link
        where da.package_name='%s' and da.version_code=%s
        ''' % (package_name.replace("'", ''), version_code)
        if debug:
            print sql.encode('utf-8')
        c.execute(sql)
        r = c.fetchall()
        if debug:
            print r
        old_links, old_update, old_labels = avail_download_links, update_note, labels

        for l in r:
            if avail_download_links and avail_download_links.find(l[0]) == -1:
                avail_download_links = '%s %s' % (avail_download_links, l[0])
            if not update_note and l[1]:
                update_note = l[1]
            if not labels and l[2]:
                labels = l[2]

        if avail_download_links == old_links \
                and update_note == old_update and labels == old_labels:
            return False, avail_download_links, update_note, labels
        return True, avail_download_links, update_note, labels
    finally:
        c.close()


def update_final_app(id, value_dict):
    try:
        c = _db.cursor()
        sql = u'update final_app set %s where id = %s'

        def normalize(v):
            return v if not v else v.replace("'", '"')
        ks, vs = [], []
        for k, v in value_dict.items():
            ks.append(k)
            vs.append(v)
        ks = [u"%s=%%s" % k for k in ks]
        ks.append(u'updated_at=current_timestamp()')
        ks.append(u'status=status&0xfffffffffffffff8')
        sql = sql % (u','.join(ks), id)
        if debug:
            print sql.encode('utf-8')
            print vs
        r = c.execute(sql, vs)
        _db.conn.commit()
        print 'updated %s rows' % r
    finally:
        c.close()


def main(count=count, id_from=None, id_to=None):
    apps = get_final_app(int(id_from or max_id), int(id_to or stop_id), count=int(count))
    handled_count = 0
    update_count = 0
    while apps:
        for app in apps:
            handled_count += 1
            print 'begin handle final_app: %s' % app[0]
            need_update, avail_download_links, update_note, labels = get_update_info(
                app[1], app[2], app[3], app[4], app[5], app[6])
            if need_update:
                update_final_app(app[0], {'avail_download_links': avail_download_links,
                                          'update_note': update_note,
                                          'labels': labels})
                update_count += 1
                print 'update final_app(id=%s)' % app[0]
            else:
                print 'final_app(id=%s) do not need to update' % app[0]
        print 'handled %s apps, updated %s apps.' % (handled_count, update_count)

        c_id = apps[len(apps) - 1][0]
        print 'will continue at id: %s' % c_id
        apps = get_final_app(c_id, int(id_to or stop_id), int(count))


def help():
    import sys
    print '%s [id_from=xx|%s] [id_to=xx|%s] [count=xx|%s] [debug=True,False|False]' % \
        (sys.argv[0], max_id, stop_id, count)


if __name__ == '__main__':
    import sys
    arg_dict = {}
    global debug
    try:
        for arg in sys.argv[1:]:
            argkv = arg.split('=')
            if argkv[0] == 'debug':
                debug = 'True' == argkv[1]
            else:
                arg_dict[argkv[0]] = argkv[1]
        main(**arg_dict)
    except Exception as e:
        help()
        import traceback
        print traceback.format_exc()
        raise e


