#-*- coding: utf-8 -*-
'''
Created on Nov 22, 2013

@author: gmliao
'''
from services.core.datasource import BaseDataSource
from services.core import datasource
from utils.net import Net

SUPPORTED_LIST_TYPES = {
    datasource.LIST_TYPE_SOFT: {
        'url': 'http://openboxcdn.mobilem.360.cn/AppStore/getTopapplist?type=1&order=down&start=%d&count=%d',
    },
    datasource.LIST_TYPE_GAME: {
        'url': 'http://openboxcdn.mobilem.360.cn/AppStore/getTopapplist?type=2&order=down&start=%d&count=%d',
    },
    # datasource.LIST_TYPE_SOFT_RECOMMEND: {
    #    'url': 'http://openbox.mobilem.360.cn/AppStore/getRecomendAppsBytype?type=1&start=%d&count=%d',
    #},
    # datasource.LIST_TYPE_GAME_RECOMMEND: {
    #    'url': 'http://openbox.mobilem.360.cn/AppStore/getRecomendAppsBytype?type=2&start=%d&count=%d',
    #},
}


FIELDS = {
    datasource.FIELD_PACKAGE_NAME: 'apkid',
    datasource.FIELD_VERSION: 'version_name',
    datasource.FIELD_VERSION_CODE: 'version_code',
    datasource.FIELD_NAME: 'baike_name',
}


_PAGE_COUNT = 30


class Zhushou360DataSource(BaseDataSource):

    NAME = 'zhushou.360.cn'

    def get_list_data(self, list_type=0, page=0, fields=None):
        if list_type not in SUPPORTED_LIST_TYPES:
            raise Exception('not supported list_type: %s' % list_type)
        list_type = SUPPORTED_LIST_TYPES[list_type]
        start = page * _PAGE_COUNT
        json_data = Net.read_json(list_type['url'] % (start, _PAGE_COUNT))
        ret = []
        if 'data' not in json_data:
            return []
        for data in json_data['data']:
            ret.append(self.json_get_data(data, fields, FIELDS))
        return ret

    def get_app_info_by_packagename(self, packagename, fields=None):
        url = 'http://openboxcdn.mobilem.360.cn/mintf/getAppInfoByIds?pname=%s&market_id=360market' % packagename
        json_data = Net.read_json(url)
        if 'data' not in json_data or len(json_data['data']) < 1:
            return None
        return self.json_get_data(json_data['data'][0], fields, FIELDS)


if __name__ == '__main__':
    ds = Zhushou360DataSource()
    fields = [datasource.FIELD_PACKAGE_NAME, datasource.FIELD_VERSION, datasource.FIELD_VERSION_CODE]
    print ds.get_list_data(datasource.LIST_TYPE_SOFT, 0, fields)
    print ds.get_app_info_by_packagename('com.dragon.android.pandaspace', fields)
    apps = ds.get_apps_from_list(200, datasource.LIST_TYPE_SOFT, fields)
    print len(apps)
    print [app[0] for app in apps]




