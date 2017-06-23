# -*- coding: utf-8 -*-
from estorecore.db import MongodbStorage


UPDATE_SERVICES = [
        {
        'update_time':'2012-10-26',
        'content_title':'test1',
        'package_name':'com.eshore.ezone',
        'title':'update-2012-10-26',
        'button':[
            {
                'action': "download",
                'btn': u"立即更新",
                'order': 1
                },
            {
                'action': "",
                'btn': u"取消",
                'order': 2
                }
            ],
        'version_code':101,
        'download_url':"http://tel-s.dolphin-browser.com/downloads/apk/EStore.apk",
        'change_log':u"""update dolphin""",
        'is_force': False,
        'version_name':"1.0.1",
        'channel_promote':False,
        'is_auto':True,
            },
        {
        'update_time':'2012-10-30',
        'content_title':'test2',
        'package_name':'com.eshore.ezone',
        'title':'update 2012-10-30',
        'button':[
            {
                'action': "",
                'btn': u"取消",
                'order': 1
                },
            {
                'action': "download",
                'btn': u"立即更新",
                'order': 2
                },
            ],
        'version_code': 102,
        'download_url':"http://tel-s.dolphin-browser.com/downloads/apk/EStore.apk",
        'change_log':u"""update estore""",
        'is_force': False,
        'version_name':"1.0.2",
        'channel_promote':False,
        'is_auto': False,
            },
        {
        'update_time':'2012-10-1',
        'content_title':'test3',
        'package_name':'com.eshore.ezone',
        'title':'update 2012-10-1',
        'button':[
            {
                'action': "",
                'btn': u"取消",
                'order': 1
                },
            {
                'action': "download",
                'btn': u"立即更新",
                'order': 2
                },

            ],
        'version_code': 100,
        'download_url':"http://tel-s.dolphin-browser.com/downloads/apk/estore.apk",
        'change_log':u"""update estore""",
        'is_force':True,
        'version_name':"1.0.0",
        'channel_promote':False,
        'is_auto':True,
            }
        ]


_FIELDS = {
        'update_time':1,
        'content_title':1,
        'package_name':1,
        'package_hash':1,
        'title':1,
        'button':1,
        'version_code': 1,
        'download_url':1,
        'change_log':1,
        'is_force':1,
        'version_name':1,
        'channel_promote':1,
        'is_auto':1,
        'device': 1,
            }

class UpdateMongodbStorage(MongodbStorage):

    db_name = "update"

    def __init__(self,conn_str):
        super(UpdateMongodbStorage, self).__init__(conn_str, self.db_name)

    # level: 0: not match; 1: broad match; 2: exact match
    def _match_level(self, device_model, target_device):
        target_device = target_device.strip()
        if not target_device:
            return 1

        reverse_target = False
        if target_device.startswith('-'):
            reverse_target = True
            target_device = target_device[1 : ]

        targets = target_device.split(',')
        for target in targets:
            target = target.strip()
            if target == device_model:
                return 0 if reverse_target else 2

        return 1 if reverse_target else 0

    def _find_best_match_update(self, apps, client_version_code, client_device_model):
        best_match_app = None
        best_match_level = 1 # min match level required
        for app in apps:
            if int(app['version_code']) <= client_version_code:
                continue

            match_level = self._match_level(client_device_model, app['device'])
            if match_level > best_match_level or (match_level == best_match_level and (best_match_app is None or int(best_match_app['version_code']) < int(app['version_code']))):
                best_match_app = app
                best_match_level = match_level
        return best_match_app

    def get_update(self, package_name, source, version_code,
                         is_auto=None, device_id=None, os=None,
                         os_version=None, resolution=None, cpu=None, device_model=None, rom=None):

        update = {'button': []}
        if package_name == "com.update":
            import random
            update = UPDATE_SERVICES[random.randint(0, len(UPDATE_SERVICES) - 1)]
        else:
            cond={
                    'package_name': package_name,
                    'source': source,
                    }
            apps = self._db.update_apps.find(cond, fields=_FIELDS)
            update = self._find_best_match_update([x for x in apps], version_code, device_model)

        if update:
            if 'device' in update:
                del update['device']
        else:
            update = {'button': []}

        return update
