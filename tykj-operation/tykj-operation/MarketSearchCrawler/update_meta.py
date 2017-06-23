# coding=UTF-8
'''
Created on Aug 29, 2013

@author: gmliao
'''

from services.db import MySQLdbWrapper
from utils.logger import logger
from utils.net import Net
import random
import sys
import os
import urllib2


sys.path.append(os.path.dirname(os.path.abspath(__file__)))


reload(sys)
sys.setdefaultencoding('utf-8')


_db = MySQLdbWrapper()
debug = True
max_id = 2426550
stop_id = 0
count = 50


def get_final_app(id_from, id_to, count, hash):
    try:
        c = _db.cursor()
        if hash > 0:
            rand_result = random.randrange(1, hash)
            sql = '''
            select id, package_name, version_code
            from final_app
            where id < %s and id >= %s and file_type='apk'
                and (labels is null or labels = '')
                and (id - %s) %% %s = %s
            order by id desc
            limit %s
            ''' % (id_from, id_to, id_to, hash, rand_result, count)
        else:
            sql = '''
            select id, package_name, version_code
            from final_app
            where id < %s and id >= %s and file_type='apk'
                and (labels is null or labels = '')
            order by id desc
            limit %s
            ''' % (id_from, id_to, count)
        logger.d(sql)
        c.execute(sql)
        result = c.fetchall()
        return result
    finally:
        c.close()


def get_last_id():
    try:
        c = _db.cursor()
        sql = '''
        insert ignore into `config` (`key`, `value`, `created_at`, `updated_at`)
        values ('update_meta_last_id', 2425920, now(), now());
        '''
        logger.d(sql)
        c.execute(sql)
        _db.conn.commit()
        sql = '''
        select value from `config` where `key`='update_meta_last_id';
        '''
        logger.d(sql)
        c.execute(sql)
        result = c.fetchone()
        return result[0]
    finally:
        c.close()


def update_last_id(last_id):
    try:
        c = _db.cursor()
        sql = '''
        update `config` set value=%s, updated_at=now() where `key`='update_meta_last_id';
        ''' % last_id
        logger.d(sql)
        c.execute(sql)
        _db.conn.commit()
    finally:
        c.close()


def getAppToUpdate(last_id=None, count=50):
    try:
        last_id = last_id if last_id else get_last_id()
        c = _db.cursor()
        sql = '''
        select id, package_name, version_code from final_app
        where id > %s limit %s
        ''' % (last_id, count)
        c.execute(sql)
        result = c.fetchall()
        return result
    finally:
        c.close()


def get_final_app_cols(pn, vc, cols):
    try:
        c = _db.cursor()
        sql = '''
        select id, %s from final_app
        where package_name='%s' and version_code=%s
        ''' % (','.join(cols), pn.replace("'", ''), vc)
        if debug:
            logger.d(sql)
        c.execute(sql)
        result = c.fetchone()
        return result
    finally:
        c.close()


def update_app(package_name, version_code, labels=None, avail_download_links=None):
    try:
        updatecols = {}
        if labels:
            updatecols['labels'] = labels
        if avail_download_links:
            updatecols['avail_download_links'] = avail_download_links
        if not updatecols.keys():
            logger.i('nothing need to update')
            return
        c = _db.cursor()
        updatecols = ["%s='%s'" % (k, updatecols[k].replace("'", '')) for k in updatecols.keys()]
        sql = '''
        update final_app set %s, status=status&0xfffffffffffffff8, updated_at=now()
        where version_code=%s and package_name='%s'
        ''' % (','.join(updatecols), version_code, package_name.replace("'", ''))
        logger.d(sql)
        ret = c.execute(sql)
        logger.i('updated %s rows.' % ret)
        _db.conn.commit()
    finally:
        c.close()


label_maps = {
    'common': {
        'ads': u'内置广告',
        'noads': u'无广告',
    },
    'wandoujia': {
        '360': u'360手机卫士',
        'tencent': u'腾讯手机管家',
        'lbe': u'LBE安全大师',
    },
}


def get_wandoujia_app_labels(pn, vc):
    url = 'http://apps.wandoujia.com/api/v1/apps/%s' % pn
    data = Net.read_json(url)
    # logger.d(simplejson.dumps(data))
    apks = []
    if 'latestApk' in data:
        apks.append(data['latestApk'])
    if 'apks' in data:
        for apk in data['apks']:
            apks.append(apk)

    def extract_labels(apk):
        securityDetail = apk['securityDetail']
        labels = []
        for d in securityDetail:
            if d['status'] == 'SAFE' and d['provider'] in label_maps['wandoujia']:
                labels.append(label_maps['wandoujia'][d['provider']])
        if 'adsType' in apk and apk['adsType'] == 'NONE':
            labels.append(label_maps['common']['noads'])
        else:
            labels.append(label_maps['common']['ads'])
        labels = ','.join(labels)
        return labels

    for apk in apks:
        if 'versionCode' in apk and str(apk['versionCode']) == str(vc):
            if 'securityDetail' in apk:
                return extract_labels(apk)
            else:
                logger.d('securityDetail not found for app(pn=%s, vc=%s)' % (pn, vc))
        else:
            logger.d('versionCode(%s) not match for app(pn=%s, vc=%s)' % (apk['versionCode'], pn, vc))
    return ''


class NoRedirectHandler(urllib2.HTTPRedirectHandler):

    def http_error_302(self, req, fp, code, msg, headers):
        result = urllib2.HTTPError(req.get_full_url(), code, msg, headers, fp)
        result.status = code
        return result
    http_error_301 = http_error_303 = http_error_307 = http_error_302

no_redirect_opener = urllib2.build_opener(NoRedirectHandler())


def get_real_url(url):
    oldurl = url
    if url.find('http://www.appchina.com') == 0:
        url = no_redirect_opener.open(url).headers.dict['location']
    if url.find('http://www.d.appchina.com') == 0:
        url = no_redirect_opener.open(url).headers.dict['location']
    logger.i('get_real_url for url(%s) return url: %s' % (oldurl, url))
    return url


def update_appchina_real_downloadlink(avail_download_links):
    logger.d(str(avail_download_links))
    if avail_download_links:
        avail_download_links = avail_download_links.split(' ')
        newurls = []
        for l in avail_download_links:
            if l.find('http://www.appchina.com') == 0 or l.find('http://www.d.appchina.com') == 0:
                try:
                    newl = get_real_url(l)
                    if newl != l and newl not in avail_download_links:
                        newurls.append(newl)
                except Exception as e:
                    logger.e('%s' % e)
        if newurls:
            for l in newurls:
                avail_download_links.append(l)
            avail_download_links = ' '.join(avail_download_links)
            logger.d(str(avail_download_links))
            return avail_download_links
        else:
            logger.d('nothing need to update.')
            return None
    else:
        logger.d('avail_download_links is empty, do not need to update.')
        return None


def update_apps_avail_download_links(apps):
    suc_count = 0
    for pn, vc in apps:
        try:
            avail_download_links = get_final_app_cols(pn, vc, ['avail_download_links'])
            if avail_download_links:
                avail_download_links = avail_download_links[1]
                avail_download_links = update_appchina_real_downloadlink(avail_download_links)
            if avail_download_links:
                update_app(pn, vc, avail_download_links=avail_download_links)
                suc_count += 1
                logger.i('update app(pn=%s, vc=%s) success.' % (pn, vc))
            else:
                logger.i('ignore app(pn=%s, vc=%s).' % (pn, vc))
        except Exception as e:
            logger.e('update app(pn=%s, vc=%s) failed: %s' % (pn, vc, e))
    return suc_count


def update_apps_labels(apps):
    suc_count = 0
    for pn, vc in apps:
        try:
            labels = get_wandoujia_app_labels(pn, vc)
            if labels:
                update_app(pn, vc, labels)
                suc_count += 1
                logger.i('update app(pn=%s, vc=%s) success.' % (pn, vc))
            else:
                logger.i('ignore app(pn=%s, vc=%s).' % (pn, vc))
        except Exception as e:
            logger.e('update app(pn=%s, vc=%s) failed: %s' % (pn, vc, e))
    return suc_count


def update_apps_inpage(id_from, id_to, count, hash):
    id_from, id_to, count, hash = int(id_from), int(id_to), int(count), int(hash)
    apps = get_final_app(id_from, id_to, count, hash)
    while apps:
        id_from = apps[len(apps) - 1][0]
        apps = [(app[1], app[2]) for app in apps]
        suc_count = update_apps_labels(apps)
        logger.i('handled %s apps. success: %s fail: %s' % (len(apps), suc_count, (len(apps) - suc_count)))
        apps = get_final_app(id_from, id_to, count, hash)


def main(apps=None, target='labels', id_from=max_id, id_to=stop_id, hash=hash, count=count):
    if not apps:
        logger.i('update_apps_inpage start...')
        update_apps_inpage(id_from, id_to, count, hash)
        logger.i('update_apps_inpage end...')
    else:
        logger.i('update_apps start...')
        apps = [a.split('-') for a in apps.split(',')]
        target = 'update_apps_%s' % target
        func = getattr(sys.modules[__name__], target)
        if callable(func):
            func(apps)
        else:
            raise Exception('attibute: %s is not callable' % func)
        logger.i('update_apps end...')


def help():
    print '%s [target=labels,avail_download_links|labels] '\
        '[apps={package_name}-{version_code},{package_name}-{version_code},...] '\
        '[id_from=xx|%s] [id_to=xx|%s] [count=xx|%s] [hash=xx|0] [debug=True,False|False]'


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



