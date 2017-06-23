#-*- coding: utf-8 -*-
'''
Created on Nov 22, 2013

@author: gmliao
'''
from services.core.datasource import BaseDataSource
from services.core import datasource
from utils.net import Net
from utils.logger import logger
from utils import jsonutils

SUPPORTED_LIST_TYPES = {
    datasource.LIST_TYPE_SOFT: {
        'url': ('http://apps.wandoujia.com/api/v1/feeds?opt_fields=adsCursor,data.app.apks.compatible,'
                'data.app.apks.incompatibleDetail,data.reason.*,data.app.title,data.app.packageName,data.app.ad,'
                'data.app.icons.px78,data.app.installedCountStr,data.app.apks.downloadUrl.url,data.app.apks.bytes,'
                'data.app.apks.verified,data.app.apks.versionName,data.app.apks.versionCode,data.app.detailParam,'
                'data.app.imprUrl,data.app.stat.weeklyStr,data.app.exclusiveBadge,data.app.apks.md5,'
                'data.app.editorComment,data.app.award.issue,data.app.apks.superior,data.app.apks.paidType'
                '&area=index&ads_start=0&start=%s&max=%s'),
    },
    datasource.LIST_TYPE_GAME: {
        'url': ('http://apps.wandoujia.com/api/v1/feeds?opt_fields=adsCursor,data.app.apks.compatible,'
                'data.app.apks.incompatibleDetail,data.reason.*,data.app.title,data.app.packageName,data.app.ad,'
                'data.app.icons.px78,data.app.installedCountStr,data.app.apks.downloadUrl.url,data.app.apks.bytes,'
                'data.app.apks.verified,data.app.apks.versionName,data.app.apks.versionCode,data.app.detailParam,'
                'data.app.imprUrl,data.app.stat.weeklyStr,data.app.exclusiveBadge,data.app.apks.md5,'
                'data.app.editorComment,data.app.award.issue,data.app.apks.superior,data.app.apks.paidType'
                '&area=game&ads_start=0&start=%s&max=%s'),
    },
    datasource.LIST_TYPE_INDEX: {
        'url': ('http://apps.wandoujia.com/api/v1/apps?opt_fields=apks.compatible,apks.incompatibleDetail,title,'
                'packageName,ad,icons.px78,installedCountStr,apks.downloadUrl.url,apks.bytes,apks.verified,'
                'apks.versionName,apks.versionCode,detailParam,imprUrl,stat.weeklyStr,exclusiveBadge,'
                'apks.md5,editorComment,apks.paidType&type=weeklytop&start=%s&max=%s'),
    },
}

FIELDS = {
    datasource.FIELD_PACKAGE_NAME: 'packageName',
    datasource.FIELD_VERSION: 'versionName',
    datasource.FIELD_VERSION_CODE: 'versionCode',
    datasource.FIELD_NAME: 'title',
}

_PAGE_COUNT = 30


class WandoujiaDataSource(BaseDataSource):

    NAME = 'wandoujia.com'

    def get_list_data(self, list_type=0, page=0, fields=None):
        if list_type not in SUPPORTED_LIST_TYPES:
            raise Exception('not supported list_type: %s' % list_type)
        list_type = SUPPORTED_LIST_TYPES[list_type]
        start = page * _PAGE_COUNT
        json_data = Net.read_json(list_type['url'] % (start, _PAGE_COUNT))
        ret = []
        if 'data' not in json_data:
            return ret
        for data in json_data['data']:
            ret.append(self._get_data(data['app'], fields))
        return ret

    def _get_data(self, data, fields, packagename=None):
        if not fields:
            return data
        ret_data = []
        for f in fields:
            fn = FIELDS[f]
            if f in [datasource.FIELD_PACKAGE_NAME, datasource.FIELD_NAME]:
                ret_data.append(packagename or data[fn])
            else:
                ret_data.append(data['apks'][0][fn])
        return ret_data

    def get_app_info_by_packagename(self, packagename, fields=None):
        url = ('http://apps.wandoujia.com/api/v1/apps/%s?opt_fields=apks.compatible,apks.incompatibleDetail,'
               'ad,apks.adsType,apks.beta,apks.bytes,apks.downloadUrl.*,apks.size,apks.versionCode,apks.versionName,'
               'apks.securityStatus,apks.md5,apks.permissionLevel,apks.superior,apks.dangerousPermissions,'
               'apks.permissions,apks.securityDetail.*,apks.resolution,categories.alias,categories.name,description,'
               'title,commentsCount,likeCount,dislikesCount,installedCountStr,icons.px78,'
               'packageName,id,likesRate,screenshots.*,apks.verified,apks.paidType')
        url = url % packagename
        try:
            json_data = Net.read_json(url)
        except Exception as e:
            logger.e('read_json from url(%s) failed: %s' % (url, e))
            return None
        if 'apks' not in json_data:
            logger.w('one or more fields(%s) can not be found in object: %s' % (fields, json_data))
            return None
        return self._get_data(json_data, fields, packagename=None)

    def get_list_packagenames(self, count=10):
        pns = set()
        for list_type in SUPPORTED_LIST_TYPES.keys():
            list_pns = self.get_list_page_packagenames(list_type, count)
            for pn in list_pns:
                pns.add(pn)
        return pns

    def get_list_page_packagenames(self, list_type, count):
        page = 0
        pns = []
        while len(pns) < count:
            apps = self.get_list_data(list_type, page)
            page += 1
            found = jsonutils.find_attr(apps, FIELDS[datasource.FIELD_PACKAGE_NAME], str)
            for pn in found:
                pns.append(pn)
            if not found:
                break
        return pns


if __name__ == '__main__':
    ds = WandoujiaDataSource()
    fields = [datasource.FIELD_PACKAGE_NAME, datasource.FIELD_VERSION, datasource.FIELD_VERSION_CODE]
    print ds.get_list_data(datasource.LIST_TYPE_SOFT, 0, fields)
    print ds.get_app_info_by_packagename('com.dragon.android.pandaspace', fields)
    print ds.get_list_packagenames()



