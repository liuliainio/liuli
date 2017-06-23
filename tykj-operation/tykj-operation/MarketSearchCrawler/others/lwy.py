#-*- coding: utf-8 -*-
'''
Created on Dec 17, 2013

@author: gmliao
'''

import sys
import time
import datetime
import traceback
reload(sys)
getattr(sys, 'setdefaultencoding')('utf8')


import requests
import simplejson
sys.stderr.write('start at: %s\n' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
r = requests.post(
    'http://admin.ztems.com/zteStoremanager/$/ssb/uiloader/loginMgt/login.ssm',
    "[{\"userId\":\"bainatemp\",\"password\":\"12345\"}]")
headers = {'Cookie': r.headers['set-cookie']}
apps = []
apps_set = set()
final_info = []
start = 0
while True:
    try:
        count = 30
        r1 = requests.post(
            'http://admin.ztems.com/zteStoremanager/zteStoremanager/appmanager/AppUpload/storeApplicationFacade/findStoreApplication.ssm',

            '[{"isBind":"1","appType":"0","operType":"2,5,6","cname":"","ownerType":"","begintime":null,"endtime":null,"appState":"","owner":"","packageName":"","downcount":"","categoryCodeTop":"","categoryCodeF":"","categoryCode":"","artist":"","songList":"","special":""},%s,%s]' % (
                start,
                count),

            headers=headers)
        r1data = simplejson.loads(r1.content)
        for d in r1data['rtn']['data']:
            if d['packageName'] not in apps_set:
                apps.append(d)
                apps_set.add(d['packageName'])
        if len(r1data['rtn']['data']) < count:
            break
        start += count
        sys.stderr.write('fetched %s app from list.\n' % len(apps))
    except Exception as e:
        sys.stderr.write(u'fetch app list data failed: %s\n' % e)
        sys.stderr.write(traceback.format_exc())
        break

count = 0
for app in apps:
    code = app['appCode']
    try:
        count = count + 1
        if count % 10 == 0:
            sys.stderr.write('fetched %s apps\n' % count)
        r2 = requests.post(
            'http://admin.ztems.com/zteStoremanager/zteStoremanager/appmanager/AppUpload/storeAppcontentFacade/findStoreAppcontentsByApp.ssm',
            '["%s"]' % code,
            headers=headers)
        r2data = simplejson.loads(r2.content)['rtn'][0]
        softid = r2data['softid']
        final_info.append({
            'pkg': app['packageName'],
            'name': app['cname'],
            'downloadurl': 'http://admin.ztems.com/zteStoremanager/servlet/download?softId=%s' % softid,
        })
        time.sleep(1)
    except Exception as e:
        sys.stderr.write('fetch app info failed: %s, %s\n' % (code, e))
        continue

sys.stderr.write('start at: %s\n' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

print 'cname\tpackage\tdownloadurl'
for app in final_info:
    print u'%s\t%s\t%s' % (app['name'], app['pkg'], app['downloadurl'])


