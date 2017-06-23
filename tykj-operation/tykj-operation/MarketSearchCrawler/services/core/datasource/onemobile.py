#-*- coding: utf-8 -*-
'''
Created on Dec 13, 2013

@author: gmliao
'''

from services.core import datasource
from services.core.datasource import BaseDataSource
from utils import jsonutils
from utils.logger import logger
from utils.net import Net


SUPPORTED_LIST_TYPE = {
    datasource.LIST_TYPE_SOFT: {
        'url': 'http://api4.1mobile.com/apps/collection/top?page=%s&order=localtop&type=0',
    },
    datasource.LIST_TYPE_SOFT_NEW: {
        'url': 'http://api4.1mobile.com/apps/collection/top?page=%s&order=localnew&type=0',
    },
    datasource.LIST_TYPE_INDEX: {
        'url': 'http://api4.1mobile.com/apps/category_name_list?type=0',
    },
    datasource.LIST_TYPE_SOFT_CATE: {
        'url': 'http://api4.1mobile.com/apps/category_app_list?id=%(id)s&order=%(type)s&page=%(page)s',
    },
}


FIELDS = {
    datasource.FIELD_NAME: 'name',
    datasource.FIELD_PACKAGE_NAME: 'id',
    datasource.FIELD_VERSION: 'version',
    datasource.FIELD_VERSION_CODE: 'versionCode',
    datasource.FIELD_ICON_LINK: 'iconURL',
    datasource.FIELD_RATING: 'stars',
    datasource.FIELD_PUBLISH_DATE: 'updateTime',
    datasource.FIELD_DOWNLOADS: 'downloadTimes',
    datasource.FIELD_DESC: 'description',
    datasource.FIELD_IMAGES: 'screenshot',
    datasource.FIELD_DOWNLOAD_LINK: 'downloadURL',
    datasource.FIELD_DEVELOPER: 'author',
    datasource.FIELD_SIZE: 'apkSize',
}


class OneMobileDataSource(BaseDataSource):

    NAME = '1mobile.com'
    cached_cate = None
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip,deflate,sdch',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Host': 'api4.1mobile.com',
        'Pragma': 'no-cache',
        'User-Agent': 'Apache HttpClient',
    }
    order_types = ['new', 'top', 'localnew', 'localtop']

    def get_list_data(self, list_type=0, page=0, fields=None, cate="0", order="new"):
        if fields is not None:
            raise NotImplementedError()
        page = page + 1
        if list_type not in SUPPORTED_LIST_TYPE:
            raise Exception('not supported list_type: %s' % list_type)
        if list_type == datasource.LIST_TYPE_INDEX:
            return self.get_cate_data()
        elif list_type in [datasource.LIST_TYPE_SOFT, datasource.LIST_TYPE_SOFT_NEW]:
            try:
                return Net.read_json(SUPPORTED_LIST_TYPE[list_type]['url'] % page, header=self.headers)['appList']
            except:
                return None
        else:
            ret = []
            url = SUPPORTED_LIST_TYPE[list_type]['url']
            try:
                ret = ret + Net.read_json(url %
                                          {'id': cate, 'type': order, 'page': page}, header=self.headers)['appList']
            except:
                return None
            return ret

    def get_cate_data(self):
        if not self.cached_cate:
            url = SUPPORTED_LIST_TYPE[datasource.LIST_TYPE_INDEX]['url']
            json_data = Net.read_json(url, header=self.headers)
            self.cached_cate = json_data['categoryList']
        return self.cached_cate


if __name__ == '__main__':
    ds = OneMobileDataSource()
    fields = None
    print ds.get_list_data(datasource.LIST_TYPE_SOFT_NEW, 0, fields)

