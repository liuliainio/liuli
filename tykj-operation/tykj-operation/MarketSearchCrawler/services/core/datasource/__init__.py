#-*- coding: utf-8 -*-
'''
Created on Sep 22, 2013

@author: gmliao
'''


LIST_TYPE_INDEX = 0
LIST_TYPE_SOFT = 1
LIST_TYPE_GAME = 2
LIST_TYPE_SOFT_NEW = 3
LIST_TYPE_GAME_NEW = 4
LIST_TYPE_SOFT_RECOMMEND = 5
LIST_TYPE_GAME_RECOMMEND = 6
LIST_TYPE_SOFT_CATE = 7
LIST_TYPE_GAME_CATE = 8


FIELD_PACKAGE_NAME = 0
FIELD_VERSION = 1
FIELD_VERSION_CODE = 2
FIELD_NAME = 3
FIELD_ICON_LINK = 4
FIELD_RATING = 5
FIELD_PUBLISH_DATE = 6
FIELD_DOWNLOADS = 7
FIELD_DESC = 8
FIELD_SCREEN_SUPPORT = 9
FIELD_IMAGES = 10
FIELD_DOWNLOAD_LINK = 11
FIELD_DEVELOPER = 12
FIELD_CATEGORY = 13
FIELD_SIZE = 14
FIELD_LANGUAGE = 15
FIELD_LABELS = 16


class BaseDataSource(object):

    def get_apps_from_list(self, count, list_type, fields, uniq=True, **kwargs):
        if uniq and FIELD_PACKAGE_NAME not in fields:
            raise Exception('FIELD_PACKAGE_NAME must in fields list')
        elif uniq:
            uniq_apps = {}
            field_idx = fields.index(FIELD_PACKAGE_NAME)
        ret = []
        page = 0
        while len(ret) < count:
            apps = self.get_list_data(list_type, page, fields, **kwargs)
            page = page + 1
            if not apps:
                break
            else:
                for app in apps:
                    if uniq:
                        pn = app[field_idx]
                        if pn in uniq_apps:
                            continue
                        else:
                            uniq_apps[pn] = ''
                    ret.append(app)
        return ret

    def get_list_data(self, list_type=0, page=0, fields=None, **kwargs):
        raise NotImplementedError()

    def get_app_info_by_id(self, app_id, fields=None):
        raise NotImplementedError()

    def get_apps_by_packagename(self, packagename_list, fields=None):
        raise NotImplementedError()

    def get_rand_apps(self, fields=None):
        raise NotImplementedError()

    def get_app_info_by_packagename(self, packagename, fields=None):
        raise NotImplementedError()

    def get_cate(self):
        raise NotImplementedError()

    def json_get_data(self, data, fields, fields_map):
        if fields:
            ret = []
            for f in fields:
                k = fields_map[f]
                if k not in data:
                    raise Exception('object has no key %s: %s' % (k, data))
                ret.append(data[k])
            return ret
        else:
            return data
