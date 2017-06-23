#-*- coding: utf-8 -*-
'''
Created on Nov 22, 2013

@author: gmliao
'''
from services.core import datasource
from services.core.datasource import BaseDataSource
from utils import jsonutils
from utils.logger import logger
from utils.net import Net


SUPPORTED_LIST_TYPES = {
    datasource.LIST_TYPE_SOFT: {
        'url': 'http://m.baidu.com/appsrv?native_api=1&action=recommend&sorttype=soft&pn=%d',
    },
    datasource.LIST_TYPE_GAME: {
        'url': 'http://m.baidu.com/appsrv?native_api=1&action=recommend&sorttype=game&pn=%d',
    },
}


FIELDS = {
    datasource.FIELD_PACKAGE_NAME: 'package',
    datasource.FIELD_VERSION: 'versionname',
    datasource.FIELD_VERSION_CODE: 'versioncode',
    datasource.FIELD_NAME: 'sname'
}


class BaiduDataSource(BaseDataSource):

    NAME = 'm.baidu.com'

    def get_list_data(self, list_type=0, page=0, fields=None):
        if list_type not in SUPPORTED_LIST_TYPES:
            raise Exception('not supported list_type: %s' % list_type)
        list_type = SUPPORTED_LIST_TYPES[list_type]
        json_data = Net.read_json(list_type['url'] % page, method='post')
        ret = []
        if 'result' not in json_data or 'data' not in json_data['result']:
            return ret
        for data in json_data['result']['data']:
            data = self._get_data(data, fields)
            if data:
                ret.append(data)
        return ret

    def _get_data(self, data, fields):
        try:
            return BaseDataSource.json_get_data(self, data, fields, FIELDS)
        except Exception as e:
            logger.e('BaiduDataSource _get_data failed: %s' % e)
            return None

    def get_app_info_by_id(self, app_id, fields=None):
        raise NotImplementedError()

    def get_app_info_by_packagename(self, packagename, fields=None):
        url = 'http://m.baidu.com/appsrv?native_api=1&pname=%s&action=detail' % packagename
        json_data = Net.read_json(url, method='post')
        if 'result' not in json_data or 'data' not in json_data['result']:
            return None
        else:
            return self._get_data(json_data['result']['data'], fields)

    def get_list_docids(self, count=10):
        list_urls = [
            'http://m.baidu.com/appsrv?action=newcomer&native_api=1&pn=%s&sorttype=game',
            'http://m.baidu.com/appsrv?action=newcomer&native_api=1&pn=%s&sorttype=soft',
            'http://m.baidu.com/appsrv?action=rank&listtype=tophot&native_api=1&pn=%s',
            'http://m.baidu.com/appsrv?action=rank&listtype=topnew&native_api=1&pn=%s',
            'http://m.baidu.com/appsrv?action=rank&listtype=topquick&native_api=1&pn=%s',
            'http://m.baidu.com/appsrv?action=rank&listtype=topscore&native_api=1&pn=%s',
            'http://m.baidu.com/appsrv?action=recommend&native_api=1&pn=%s&sorttype=game',
            'http://m.baidu.com/appsrv?action=recommend&native_api=1&pn=%s&sorttype=recommend',
            'http://m.baidu.com/appsrv?action=recommend&native_api=1&pn=%s&sorttype=soft',
            'http://m.baidu.com/appsrv?action=today&native_api=1&pn=%s',
        ]
        docids = set()
        for url in list_urls:
            list_docids = self.get_list_page_docids(url, count)
            for docid in list_docids:
                docids.add(docid)
        return docids

    def get_list_page_docids(self, url, count):
        page = 0
        docids = []
        while len(docids) < count:
            apps = Net.read_json(url % page, method='post')
            page += 1
            found = jsonutils.find_attr(apps, 'docid', (str, int))
            for docid in found:
                docids.append(docid)
            if not found:
                break
        return docids


if __name__ == '__main__':
    ds = BaiduDataSource()
    fields = [datasource.FIELD_PACKAGE_NAME, datasource.FIELD_VERSION, datasource.FIELD_VERSION_CODE]
    print ds.get_list_data(datasource.LIST_TYPE_SOFT, 0, fields)
    print ds.get_app_info_by_packagename('com.dragon.android.pandaspace', fields)
    print ds.get_list_docids()











