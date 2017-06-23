# coding=utf-8
'''
Created on Jun 20, 2011

@author: yan
'''
from MarketSearch import service
from MarketSearch.gen.ttypes import Status, LinkStatus, LinkType
from MarketSearch.spiders.base import AppSpider
from MarketSearch.spiders.itemloaders import *
from MarketSearch.spiders.scriptprocessors import BaiduScriptProcessor, \
    NduoaScriptProcessor, AppChinaScriptProcessor, HiApkScriptProcessor, \
    GoogleScriptProcessor, YoutubeScriptProcessor, YelpScriptProcessor,\
    OneMobileScriptProcessor
from MarketSearch.spiders.sourcefilterprocessors import \
    AppChinaSourceFilterProcessor
from MarketSearch.spiders.sourcelinkprocessors import BaiduSourceLinkProcessor, \
    NduoaSourceLinkProcessor, AppChinaSourceLinkProcessor, HiApkSourceLinkProcessor, \
    GoogleSourceLinkProcessor, YoutubeSourceLinkProcessor, YelpSourceLinkProcessor,\
    OneMobileLinkProcessor
from scrapy.http import Request
from utils import jsonutils
import json
import re
from scrapy.spider import BaseSpider
from services.core.datasource import onemobile
from services.core.datasource.onemobile import OneMobileDataSource
from services.core import datasource
from MarketSearch.utils import get_epoch_datetime
from MarketSearch.spiders.redirectprocessors import ThreeGRedirectProcessor, RedirectShoujiBaiduProcessor
from scrapy.item import Item
import urllib
from MarketSearch.db import market
import os
from scrapy.contrib.spiders.crawl import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
import simplejson
from MarketSearch.items import DownloadLinkItem


def _matches(url, regexs):
    for r in regexs:
        if r.search(url):
            return True
    return False


class BaiduSpider(AppSpider):

    name = "as.baidu.com"
    #itemloader_class = BaiduItemLoader
    itemloader_class = ShoujiBaiduItemLoader
    sourcelinkprocessor_class = BaiduSourceLinkProcessor
    scriptprocessor_class = BaiduScriptProcessor

    item_regexs = [re.compile(r'^http://shouji.baidu.com/soft/item\?docid=[0-9]+.*'),
                   re.compile(r'^http://shouji.baidu.com/software/item\?docid=[0-9]+.*'),
                   re.compile(r'^http://shouji.baidu.com/game/item\?docid=[0-9]+.*')]
    item_zhushou_regexs = [re.compile(r'^http://m.baidu.com/appsrv\?.*')]

    def __init__(self, name=None, **kwarg):
        super(BaiduSpider, self).__init__(name, **kwarg)

        
    def get_callback(self, link):
        if _matches(link, self.item_regexs):
            return self.parse_item
        elif _matches(link, self.item_zhushou_regexs):
            return self.parse_zhushou_cate
        else:
            return self.parse

    def parse_zhushou_cate(self, response):
        meta = response.request.meta
        source = meta['domain']
        url = response.request.url
        import simplejson
        data = simplejson.loads(response.body)
        # docids = [d['docid'] for d in data['result']['data']] if 'data' in data['result'] else []
        docids = jsonutils.find_attr(data, 'docid', (str, int))
        urls = ['http://as.baidu.com/a/item?docid=%s' % i for i in docids]

        if urls:
            if self.name.startswith('update.'):
                service.report_update_status([LinkStatus(u, source, Status.FOUND, LinkType.LEAF) for u in urls])
                service.report_update_status([LinkStatus(url, source, Status.SUCCEED, LinkType.CATELOG, len(urls))])
            else:
                service.report_status([LinkStatus(u, source, Status.FOUND, LinkType.LEAF) for u in urls])
                service.report_status([LinkStatus(url, source, Status.SUCCEED, LinkType.CATELOG, len(urls))])

    def get_rule_list(self):
        return [
            {
                'allow': r'^http://as.baidu.com/a/item\?docid=[0-9]+.*',
                'process_links': 'process_links',
                'check_url': True,
            },
            {
                'allow': r'^http://shouji.baidu.com/game/item\?docid=.*',
                'process_links': 'process_links',
                'check_url': True,
            },
            {
                'allow': r'^http://shouji.baidu.com/soft/item\?docid=.*',
                'process_links': 'process_links',
                'check_url': True,
            },
            {
                'allow': r'^http://shouji.baidu.com/software/item\?docid=.*',
                'process_links': 'process_links',
                'check_url': True,
            },

            {
                'allow': r'^http://shouji.baidu.com/game/list\?cid=.*',
                'process_links': 'process_links',
                'check_url': False,
                'link_type': LinkType.CATELOG,
            },
            {
                'allow': r'^http://shouji.baidu.com/software/list\?cid=.*',
                'process_links': 'process_links',
                'check_url': False,
                'link_type': LinkType.CATELOG,
            },
            {
                'allow': r'^http://as.baidu.com/a/software\?cid=.*',
                'process_links': 'process_links',
                'check_url': False,
                'link_type': LinkType.CATELOG,
            },
            {
                'allow': r'^http://as.baidu.com/a/rank\?cid=.*',
                'process_links': 'process_links',
                'check_url': False,
                'link_type': LinkType.CATELOG,
            },
            {
                'allow': r'^http://m.baidu.com/appsrv\?listtype=topnew.*',
                'process_links': 'process_links',
                'check_url': False,
                'link_type': LinkType.CATELOG,
            },
        ]


class UpdateBaiduSpider(BaiduSpider):

    name = "update.as.baidu.com"
    
    item_regexs = [re.compile(r'^http://shouji.baidu.com/soft/item\?docid=[0-9]+.*'),
                   re.compile(r'^http://shouji.baidu.com/software/item\?docid=[0-9]+.*'),
                   re.compile(r'^http://shouji.baidu.com/game/item\?docid=[0-9]+.*')]

    # item_regexs = [re.compile(r'^http://as.baidu.com/a/item\?docid=[0-9]+.*')]

    def __init__(self, name=None, **kwarg):
        super(UpdateBaiduSpider, self).__init__(name, **kwarg)

    def get_rule_list(self):
        return [
            {
                'allow': r'^http://shouji.baidu.com/game/item\?docid=.*',
                'process_links': 'process_links',
                'check_url': True,
            },
            {
                'allow': r'^http://shouji.baidu.com/soft/item\?docid=.*',
                'process_links': 'process_links',
                'check_url': True,
            },
            {
                'allow': r'^http://shouji.baidu.com/software/item\?docid=.*',
                'process_links': 'process_links',
                'check_url': True,
            },
            {
                'allow': r'^http://shouji.baidu.com/game/list\?cid=.*',
                'process_links': 'process_links',
                'check_url': False,
                'link_type': LinkType.CATELOG,
            },
            {
                'allow': r'^http://shouji.baidu.com/software/list\?cid=.*',
                'process_links': 'process_links',
                'check_url': False,
                'link_type': LinkType.CATELOG,
            },
            {
                'allow': r'^http://as.baidu.com/a/item\?docid=[0-9]+.*',
                'process_links': 'process_links',
                'check_url': True,
            },
            {
                'allow': r'^http://as.baidu.com/a/item\?docid=[0-9]+.*',
                'process_links': 'process_links',
                'check_url': True,
            },
            {
                'allow': r'^http://m.baidu.com/appsrv\?listtype=topnew.*',
                'process_links': 'process_links',
                'check_url': False,
                'link_type': LinkType.CATELOG,
            },
            {
                'allow': r'^http://as.baidu.com/a/rank\?cid=.*',
                'process_links': 'process_links',
                'check_url': False,
                'link_type': LinkType.CATELOG,
           },
           {
               'allow': r'^http://as.baidu.com/a/asgame\?cid=.*',
               'process_links': 'process_links',
               'check_url': False,
               'link_type': LinkType.CATELOG,
           },
           {
               'allow': r'^http://as.baidu.com/a/software\?cid=.*',
               'process_links': 'process_links',
               'check_url': False,
               'link_type': LinkType.CATELOG,
           },
        ]


class OneMobileAPISpider(BaseSpider):
    name = "api.1mobile.com"
    redirectprocessor_class = ThreeGRedirectProcessor

    def __init__(self):
        base_url = 'http://www.google.com/?'
        ds = OneMobileDataSource()
        cates = ds.get_cate_data()
        self.start_urls = []
        for c in cates:
            if str(c['categoryId']) == '0':
                continue
            param = {
                'id': c['categoryId'],
                'name': c['categoryName'],
            }
            for ot in ds.order_types:
                param1 = param.copy()
                param1.update({
                    'type': ot,
                })
                for p in range(1, 20):
                    param2 = param1.copy()
                    param2.update({
                        'page': p,
                    })
                    self.start_urls.append(base_url + '&'.join(['%s=%s' % (k, v) for k, v in param2.items()]))
                    # return

    def parse(self, response):
        url = response.meta['redirect_urls'][0] if 'redirect_urls' in response.meta else response.url
        url = url[url.find('?') + 1:]
        params = dict([p.split('=') for p in url.split('&')])
        params['name'] = urllib.unquote(params['name'])
        ds = OneMobileDataSource()
        if str(params['id']) == '0':
            yield None
            return
        apps = ds.get_list_data(
            datasource.LIST_TYPE_SOFT_CATE,
            int(params['page']),
            cate=params['id'],
            order=params['type'])
        for app in apps:
            yield self.parse_item(app, params)

    def parse_item(self, app, param):
        item = {
            'name': app[onemobile.FIELDS[datasource.FIELD_NAME]],
            'icon_link': app[onemobile.FIELDS[datasource.FIELD_ICON_LINK]],
            'publish_date': app[onemobile.FIELDS[datasource.FIELD_PUBLISH_DATE]],
            'category': param['name'],
            'downloads': app[onemobile.FIELDS[datasource.FIELD_DOWNLOADS]],
            'description': app[onemobile.FIELDS[datasource.FIELD_DESC]],
            'images': ' '.join(app[onemobile.FIELDS[datasource.FIELD_IMAGES]]),
            'developer': app[onemobile.FIELDS[datasource.FIELD_DEVELOPER]],
            'version': app[onemobile.FIELDS[datasource.FIELD_VERSION]],
            'rating': self.get_rating(app[onemobile.FIELDS[datasource.FIELD_RATING]]),
            'apk_size': app[onemobile.FIELDS[datasource.FIELD_SIZE]],
            'download_link': app[onemobile.FIELDS[datasource.FIELD_DOWNLOAD_LINK]],
            'source_link': self.get_source_link(app, param),
            'source': self.name,
        }
        spideritem = AppItem()
        for k, v in item.items():
            spideritem[k] = v
        return spideritem

    def get_source_link(self, app, param):
        pkg = app[onemobile.FIELDS[datasource.FIELD_PACKAGE_NAME]]
        vc = app[onemobile.FIELDS[datasource.FIELD_VERSION_CODE]]
        url = onemobile.SUPPORTED_LIST_TYPE[datasource.LIST_TYPE_SOFT_CATE]['url']
        return 'http://api4.1mobile.com/apps?pkg=%s&vc=%s' % (url % param, pkg, vc)

    def get_rating(self, rating):
        # print 'parse rating from %s' % rating
        mark_total = 0
        user_total = 0
        for k, v in rating.items():
            mark_total += int(k) * int(v)
            user_total += int(v)
        return '%.2f' % (mark_total / float(user_total or 1))


class OneMobileSpider(AppSpider):
    name = "1mobile.com"
    itemloader_class = OneMobileItemLoader
    item_regexs = [re.compile(r'^http://www.1mobile.com/[\w-]+-[\d]+.html')]
    sourcelinkprocessor_class = OneMobileLinkProcessor
    scriptprocessor_class = OneMobileScriptProcessor

    def __init__(self, name=None, **kwargs):
        AppSpider.__init__(self, name, **kwargs)

    def get_callback(self, link):
        if _matches(link, self.item_regexs):
            return self.parse_item
        else:
            return self.parse

    def get_rule_list(self):
        return [
            {
                'allow': r'^http://www.1mobile.com/(apps|games|downloads)/[^/]+/([0-9]+.html){0,1}$',
                'process_links': 'process_links',
                'check_url': False,
                'link_type': LinkType.CATELOG,
            },
            {
                'allow': r'^http://www.1mobile.com/[\w-]+-[\d]+.html',
                'process_links': 'process_links',
                'check_url': True,
            },
        ]


class QihuSpider(AppSpider):

    name = "zhushou.360.cn"
    itemloader_class = QihuItemLoader

    item_regexs = [re.compile(r'^http://zhushou.360.cn/detail/index/soft_id/[0-9]+$')]

    def __init__(self, name=None, **kwarg):
        super(QihuSpider, self).__init__(name, **kwarg)

    def get_callback(self, link):
        return self.parse_item if _matches(link, self.item_regexs) else self.parse

    def get_rule_list(self):
        return [
            {
                'allow': r'^http://zhushou.360.cn/detail/index/soft_id/[0-9]+$',
                'check_url': True,
            },
            {
                'allow': r'^http://zhushou.360.cn/list/index/cid/[1,2]$',
                'check_url': True,
            },
            {
                'allow': r'^http://zhushou.360.cn/list/index/cid/[1,2]?page=[0-9]+$',
                'check_url': True,
            },
        ]


class UpdateQihuSpider(QihuSpider):

    name = "update.zhushou.360.cn"

    def __init__(self, name=None, **kwarg):
        super(UpdateQihuSpider, self).__init__(name, **kwarg)

    def get_rule_list(self):
        return [
            {
                'allow': r'^http://zhushou.360.cn/detail/index/soft_id/[0-9]+$',
                'check_url': True,
            },
        ]

    def parse_item(self, response):
        item = super(UpdateQihuSpider, self).parse_item(response)
        if item and item.get('description', None):
            desc = item.get('description')
            idx = desc.find(u'【更新内容】')
            item['update_note'] = desc[idx + 6:] if idx != -1 else ''
            item['update_note'] = item['update_note'].replace('<br>', '\n')
            item['update_note'] = item['update_note'].replace('</div>', '')
            item['update_note'] = item['update_note'].replace('</div', '')
        return item


class NineOneIPhoneSpider(AppSpider):

    name = "ipa.91.com"
    itemloader_class = NineOneIphoneItemLoader
    item_regexs = [re.compile(r'^http://app.91.com/Soft/iPhone/.*\.html$')]

    def __init__(self, name=None, **kwarg):
        super(NineOneIPhoneSpider, self).__init__(name, **kwarg)

    def _create_request(self, link):
        meta = {
            'domain': self.get_domain(),
            'rules': self.get_rule_list(),
            #'dont_redirect': True,
        }
        callback = self.get_callback(link)
        return Request(url=link, callback=callback, meta=meta,
                       cookies={"BrandName": "%u82F9%u679C", "MobileTypeId": 16,
                                "MobileTypeName": "iPhone%203GS%2016G", "MobileOsId": 1},
                       headers={"Host": "app.91.com"})

    def get_callback(self, link):
        return self.parse_item if _matches(link, self.item_regexs) else self.parse

    def get_rule_list(self):
        return [
            {
                'allow': r'^http://app.91.com/Soft/iPhone/.*\.html$',
                'process_links': 'process_links',
                'check_url': True,
            },
            {
                'allow': r'^http://app.91.com/Soft/iPhone/list/[0-9]+_[0-9]+_[5,3,14]$',
                'process_links': 'process_links',
                'check_url': False,
            },
            {
                'allow': r'^http://app.91.com/soft/iPhone/list/[0-9]+_[0-9]+_[5,3,14]$',
                'process_links': 'process_links',
                'check_url': False,
            },
            {
                'allow': r'^http://app.91.com/Soft/iPad/list/[0-9]+_[0-9]+_[5,3,14]$',
                'process_links': 'process_links',
                'check_url': False,
            },
            {
                'allow': r'^http://app.91.com/soft/iPad/list/[0-9]+_[0-9]+_[5,3,14]$',
                'process_links': 'process_links',
                'check_url': False,
            },
        ]


class NineOneIPadSpider(AppSpider):

    name = "ipad.91.com"
    itemloader_class = NineOneIphoneItemLoader
    item_regexs = [re.compile(r'^http://app.91.com/Soft/iPhone/.*\.html$')]

    def __init__(self, name=None, **kwarg):
        super(NineOneIPadSpider, self).__init__(name, **kwarg)

    def _create_request(self, link):
        meta = {
            'domain': self.get_domain(),
            'rules': self.get_rule_list(),
            #'dont_redirect': True,
        }
        callback = self.get_callback(link)
        return Request(url=link, callback=callback, meta=meta,
                       cookies={"iPadFlag": "true", "BrandName": "%u82F9%u679C", "MobileTypeId": 2175,
                                "MobileTypeName": "iPad", "MobileOsId": 1},
                       headers={"Host": "app.91.com"})

    def get_callback(self, link):
        return self.parse_item if _matches(link, self.item_regexs) else self.parse

    def get_rule_list(self):
        return [
            {
                'allow': r'^http://app.91.com/Soft/iPhone/.*\.html$',
                'process_links': 'process_links',
                'check_url': True,
            },
            {
                'allow': r'^http://app.91.com/Soft/iPhone/list/[0-9]+_[0-9]+_[5,3,14]$',
                'process_links': 'process_links',
                'check_url': False,
            },
            {
                'allow': r'^http://app.91.com/soft/iPhone/list/[0-9]+_[0-9]+_[5,3,14]$',
                'process_links': 'process_links',
                'check_url': False,
            },
            {
                'allow': r'^http://app.91.com/Soft/iPad/list/[0-9]+_[0-9]+_[5,3,14]$',
                'process_links': 'process_links',
                'check_url': False,
            },
            {
                'allow': r'^http://app.91.com/soft/iPad/list/[0-9]+_[0-9]+_[5,3,14]$',
                'process_links': 'process_links',
                'check_url': False,
            },
        ]


class XiaomiThemeSpider(AppSpider):

    name = "zhuti.xiaomi.com"
    itemloader_class = XiaomiThemeItemLoader
    item_regexs = [re.compile(r'^http://zhuti.xiaomi.com/detail/.*$')]

    def __init__(self, name=None, **kwarg):
        super(XiaomiThemeSpider, self).__init__(name, **kwarg)

    def get_callback(self, link):
        return self.parse_item if _matches(link, self.item_regexs) else self.parse

    def get_rule_list(self):
        return [
            {
                'allow': r'^http://zhuti.xiaomi.com/detail/.*$',
                'process_links': 'process_links',
                'check_url': True,
            },
            {
                'allow': r'^http://zhuti.xiaomi.com/(compound|icon|lockstyle|font)\?page=[0-9]+&sort=(New|Hot)$',
                'process_links': 'process_links',
                'check_url': False,
                'link_type': LinkType.CATELOG,
            },
        ]


class XiaomiImageSpider(AppSpider):

    name = "image.xiaomi.com"
    itemloader_class = XiaomiThemeItemLoader
    item_regexs = [re.compile(r'^http://zhuti.xiaomi.com/detail/.*$')]

    def __init__(self, name=None, **kwarg):
        super(XiaomiThemeSpider, self).__init__(name, **kwarg)

    def get_callback(self, link):
        return self.parse_item if _matches(link, self.item_regexs) else self.parse

    def get_rule_list(self):
        return [
            {
                'allow': r'^http://zhuti.xiaomi.com/detail/.*$',
                'process_links': 'process_links',
                'check_url': True,
            },
            {
                'allow': r'^http://zhuti.xiaomi.com/(compound|icon|lockstyle|font)\?page=[0-9]+&sort=(New|Hot)$',
                'process_links': 'process_links',
                'check_url': False,
                'link_type': LinkType.CATELOG,
            },
        ]


class NineOneSpider(AppSpider):

    name = "91.com"
    itemloader_class = NineOneItemLoader
    item_regexs = [re.compile(r'^http://mobile.91.com/Theme/Android/[0-9]+.html$')]

    def __init__(self, name=None, **kwarg):
        super(NineOneSpider, self).__init__(name, **kwarg)

    def get_callback(self, link):
        return self.parse_item if _matches(link, self.item_regexs) else self.parse

    def get_rule_list(self):
        return [
            {
                'allow': r'^http://mobile.91.com/Theme/Android/[0-9]+.html$',
                'process_links': 'process_links',
                'check_url': True,
            },
            {
                'allow': r'^http://mobile.91.com/theme/Android/list/cate_[0-9]+/[0-9]+_[0-9]+.html$',
                'process_links': 'process_links',
                'check_url': False,
                'link_type': LinkType.CATELOG,
            },
            {
                'allow': r'^http://mobile.91.com/Theme/Android/list/[0-9]+_[0-9]+_0$',
                'process_links': 'process_links',
                'check_url': False,
                'link_type': LinkType.CATELOG,
            },
        ]


class NineOneImageSpider(AppSpider):

    name = "image.91.com"
    itemloader_class = NineOneImageItemLoader
    item_regexs = [re.compile(r'http://mobile.91.com/Pic/[0-9]+.html$')]

    def __init__(self, name=None, **kwarg):
        super(NineOneImageSpider, self).__init__(name, **kwarg)

    def _create_request(self, link):
        meta = {
            'domain': self.get_domain(),
            'rules': self.get_rule_list(),
            #'dont_redirect': True,
        }
        callback = self.get_callback(link)
        return Request(url=link, callback=callback, meta=meta,
                       cookies={"BrandName": "HTC", "MobileTypeId": 20,
                                "MobileTypeName": "Magic%28G2%29",
                                "MobileOsId": 9},
                       headers={"Host": "mobile.91.com"})

    def get_callback(self, link):
        return self.parse_item if _matches(link, self.item_regexs) else self.parse

    def get_rule_list(self):
        return [
            {
                'allow': r'http://mobile.91.com/Pic/[0-9]+.html$',
                'process_links': 'process_links',
                'check_url': True,
            },
            {
                'allow': r'^http://mobile.91.com/pic/list/[0-9]+_[0-9]+_0$',
                'process_links': 'process_links',
                'check_url': False,
                'link_type': LinkType.CATELOG,
            },
        ]


class HiApkSpider(AppSpider):

    name = "hiapk.com"
    itemloader_class = HiApkItemLoader
    scriptprocessor_class = HiApkScriptProcessor
    sourcelinkprocessor_class = HiApkSourceLinkProcessor
    item_regexs = [re.compile(r'apk.hiapk.com/html/[0-9]{4}/[0-9]{2}/[0-9]+\.html$')]

    def __init__(self, name=None, **kwarg):
        super(HiApkSpider, self).__init__(name, **kwarg)

    def get_callback(self, link):
        return self.parse_item if _matches(link, self.item_regexs) else self.parse

    def get_rule_list(self):
        return [
            {
                'allow': r'apk.hiapk.com/html/[0-9]{4}/[0-9]{2}/[0-9]+\.html(.*)',
                'process_links': 'process_links',
                'check_url': True,
            },
            {
                'allow': r'^http://apk.hiapk.com/(apps|games)(.*)#[0-9]_1_0_0_0_0_0$',
                'process_links': 'process_links',
                'check_url': False,
                'link_type': LinkType.CATELOG,
            },
        ]


class UpdateHiApkSpider(HiApkSpider):

    name = "update.hiapk.com"

    def __init__(self, name=None, **kwarg):
        super(UpdateHiApkSpider, self).__init__(name, **kwarg)

    def get_rule_list(self):
        return [
            {
                'allow': r'apk.hiapk.com/html/[0-9]{4}/[0-9]{2}/[0-9]+\.html(.*)',
                'process_links': 'process_links',
                'check_url': True,
            },
        ]


class AppChinaSpider(AppSpider):

    name = "appchina.com"
    itemloader_class = AppChinaItemLoader
    sourcelinkprocessor_class = AppChinaSourceLinkProcessor
    scriptprocessor_class = AppChinaScriptProcessor
    sourcefilterprocessor_class = AppChinaSourceFilterProcessor

    item_regexs = [re.compile(r'^http://www.appchina.com/app/+(.*)')]

    def __init__(self, name=None, **kwarg):
        super(AppChinaSpider, self).__init__(name, **kwarg)

    def get_callback(self, link):
        return self.parse_item if _matches(link, self.item_regexs) else self.parse

    def get_rule_list(self):
        return [
            {
                'allow': r'^http://www.appchina.com/app/+(.*)',
                'process_links': 'process_links',
                'check_url': True,
            },
            {
                'allow': r'^http://www.appchina.com/category/[0-9]+(/0_0_[0-9]+_1_0_0_0\.|\.)html',
                'process_links': 'process_links',
                'check_url': True,
                'link_type': LinkType.CATELOG,
            },
            {
                'allow': r'^http://www.appchina.com/post/(.*)\.html',
                'process_links': 'process_links',
                'check_url': True,
                'link_type': LinkType.CATELOG,
            },
        ]


class UpdateAppChinaSpider(AppChinaSpider):

    name = "update.appchina.com"

    def __init__(self, name=None, **kwarg):
        super(UpdateAppChinaSpider, self).__init__(name, **kwarg)

    def get_rule_list(self):
        return [
            {
                'allow': r'^http://www.appchina.com/app/+(.*)',
                'process_links': 'process_links',
                'check_url': True,
            },
        ]


class GoApkSpider(AppSpider):

    name = "goapk.com"
    itemloader_class = GoApkItemLoader
    item_regexs = [re.compile(r'/soft_[0-9]+.html$')]

    def __init__(self, name=None, **kwarg):
        super(GoApkSpider, self).__init__(name, **kwarg)

    def get_callback(self, link):
        return self.parse_item if _matches(link, self.item_regexs) else self.parse

    def get_rule_list(self):
        return [
            {
                'allow': r'/soft_[0-9]+.html$',
                'check_url': True,
            },
            {
                'allow': r'/sort_[0-9]+_[0-9]+(.*).html$',
                'check_url': True,
                'link_type': LinkType.CATELOG,
            },
        ]


class UpdateGoApkSpider(GoApkSpider):

    name = "update.goapk.com"

    def __init__(self, name=None, **kwarg):
        super(UpdateGoApkSpider, self).__init__(name, **kwarg)

    def get_rule_list(self):
        return [
            {
                'allow': r'/soft_[0-9]+.html$',
                'check_url': True,
            },
        ]


class NDuoASpider(AppSpider):

    name = "nduoa.com"
    itemloader_class = NDuoAItemLoader
    scriptprocessor_class = NduoaScriptProcessor
    sourcelinkprocessor_class = NduoaSourceLinkProcessor
    item_regexs = [re.compile(r'^http://www.nduoa.com/apk/detail/[0-9]+$')]

    def __init__(self, name=None, **kwarg):
        super(NDuoASpider, self).__init__(name, **kwarg)

    def get_callback(self, link):
        return self.parse_item if _matches(link, self.item_regexs) else self.parse

    def get_rule_list(self):
        return [
            {
                'allow': r'^http://www.nduoa.com/apk/detail/[0-9]+$',
                'process_links': 'process_links',
                'check_url': True,
            },
            {
                'allow': r'^http://www.nduoa.com/cat[0-9]+$',
                'process_links': 'process_links',
                'check_url': True,
                'link_type': LinkType.CATELOG,
            },
            {
                'allow': r'^http://www.nduoa.com/cat[0-9]+\?&page=[0-9]+$',
                'process_links': 'process_links',
                'check_url': True,
                'link_type': LinkType.CATELOG,
            },
        ]


class UpdateNDuoASpider(NDuoASpider):

    name = "update.nduoa.com"

    def __init__(self, name=None, **kwarg):
        super(UpdateNDuoASpider, self).__init__(name, **kwarg)

    def get_rule_list(self):
        return [
            {
                'allow': r'^http://www.nduoa.com/apk/detail/[0-9]+$',
                'process_links': 'process_links',
                'check_url': True,
            },
        ]


class MumayiSpider(AppSpider):

    name = "mumayi.com"
    itemloader_class = MumayiItemLoader
    item_regexs = [re.compile(r'/android-[0-9]+.html')]

    def __init__(self, name=None, **kwarg):
        super(MumayiSpider, self).__init__(name, **kwarg)

    def get_callback(self, link):
        return self.parse_item if _matches(link, self.item_regexs) else self.parse

    def get_rule_list(self):
        return [
            {
                'allow': r'/android-[0-9]+.html',
                'check_url': True,
            },
            {
                'allow': r'/android/[a-zA-Z]+(/list_[0-9]+_[0-9]+.html)?',
                'check_url': True,
                'link_type': LinkType.CATELOG,
            },
        ]


class UpdateMumayiSpider(MumayiSpider):

    name = "update.mumayi.com"

    def __init__(self, name=None, **kwarg):
        super(UpdateMumayiSpider, self).__init__(name, **kwarg)

    def get_rule_list(self):
        return [
            {
                'allow': r'/android-[0-9]+.html',
                'check_url': True,
            },
        ]


class GoogleSpider(AppSpider):

    name = "market.android.com"
    itemloader_class = GoogleItemLoader
    sourcelinkprocessor_class = GoogleSourceLinkProcessor
    scriptprocessor_class = GoogleScriptProcessor

    item_regexs = [
        re.compile(r'^https://play.google.com/store/apps/details\?id=\w+\.(.*)'),
        re.compile(r'^https://play.google.com/store/apps/details\?id=\w+\.(.*)&feature=(.*)'),
        re.compile(r'^https://play.google.com/store/apps/details\?feature=(.*)&id=\w+\.(.*)')
    ]

    def __init__(self, name=None, **kwarg):
#        self.DEFAULT_REQUEST_HEADERS = {'Accept-Language': 'en_US'}
        super(GoogleSpider, self).__init__(name, **kwarg)

    def get_callback(self, link):
        return self.parse_item if _matches(link, self.item_regexs) else self.parse

    def get_rule_list(self):
        return [
            {
                'allow': r'^https://play.google.com/store/apps/details\?id=\w+\.(.*)',
                'process_links': 'process_links',
                'check_url': True,
            },
            {
                'allow': r'^https://play.google.com/store/apps/details\?feature=(.*)&id=\w+\.(.*)',
                'process_links': 'process_links',
                'check_url': True,
            },
            {
                'allow': r'^https://play.google.com/store/apps/details\?id=\w+\.(.*)&feature=(.*)',
                'process_links': 'process_links',
                'check_url': True,
            },
            {
                'allow': r'^https://play.google.com/store/apps/details\?feature=(.*)&id=apps_(.*)',
                'process_links': 'process_links',
                'check_url': True,
                'link_type': LinkType.CATELOG,
            },
            {
                'allow': r'^https://play.google.com/store/apps/details\?id=apps_(.*)',
                'process_links': 'process_links',
                'check_url': True,
                'link_type': LinkType.CATELOG,
            },
            {
                'allow': r'^https://play.google.com/store/apps/(.*)',
                'process_links': 'process_links',
                'check_url': True,
                'link_type': LinkType.CATELOG,
            }
        ]


class GooglePlaySpider(GoogleSpider):
    name = "play.google.com"
    itemloader_class = GooglePlayItemLoader

    def __init__(self, name=None, **kwarg):
        self.start_urls = ['https://play.google.com/store/apps/details?id=com.fifa.fifaapp.android']
        self.start_urls = ['https://play.google.com/store']
        urlname = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'india_topapps')
        self.start_urls = ['https://play.google.com/store/apps/details?id=%s' %
                           line[0:line.find("'")] for line in file(urlname)]
        #self.start_urls = [self.start_urls[0]]
        self.DEFAULT_REQUEST_HEADERS = {'Accept-Language': 'en_US'}
        GoogleSpider.__init__(self, name=None, **kwarg)

    def is_item_valid(self, item, level=0):
        '''
        At least source and source link are present, so an item is valid only it has more attributes loaded.
        '''
        if level == 0:
            if len(item._values) <= 2:
                return False

        if level == 1:
            # check item count
            if len(item._values) < 9:
                market.report_link(item['source'], 'mass_null', item['source_link'])
                return False

            # check key item
#            if not 'name' in item or not 'version' in item or not 'download_link' in item:
            if not 'name' in item or not 'version' in item \
                    or not 'publish_date' in item:
                market.report_link(item['source'], 'missing_key', item['source_link'])
                return False

            # check image and icon, just warning, so not return False
            if not 'images' in item or item['images'] == '':
                market.report_link(item['source'], 'missing_image', item['source_link'])
            if not 'icon_link' in item or item['icon_link'] == '':
                market.report_link(item['source'], 'missing_icon', item['source_link'])

        return True


class YoutubeSpider(AppSpider):

    name = "youtube.com"
    itemloader_class = YoutubeItemLoader
    sourcelinkprocessor_class = YoutubeSourceLinkProcessor
    scriptprocessor_class = YoutubeScriptProcessor

    item_regexs = [re.compile(r'^http://www.youtube.com/watch\?v=+(.*)')]

    def __init__(self, name=None, **kwarg):
        super(YoutubeSpider, self).__init__(name, **kwarg)

    def get_callback(self, link):
        return self.parse_item if _matches(link, self.item_regexs) else self.parse

    def get_rule_list(self):
        return [
            {
                'allow': r'^http://www.youtube.com/watch\?v=+(.*)',
                'process_links': 'process_links',
                'check_url': True,
            },
            {
                'allow': r'^http://www.youtube.com/channel/+(.*)',
                'process_links': 'process_links',
                'check_url': True,
                'link_type': LinkType.CATELOG,
            },
            {
                'allow': r'^http://www.youtube.com/playlist+(.*)',
                'process_links': 'process_links',
                'check_url': True,
                'link_type': LinkType.CATELOG,
            },
            {
                'allow': r'^http://www.youtube.com/([a-z]*)',
                'process_links': 'process_links',
                'check_url': True,
                'link_type': LinkType.CATELOG,
            },
        ]


class YelpSpider(AppSpider):

    name = "yelp.com"
    itemloader_class = YelpItemLoader
    sourcelinkprocessor_class = YelpSourceLinkProcessor
    scriptprocessor_class = YelpScriptProcessor
    item_regexs = [re.compile(r'^http://www.yelp.com/biz/+(.*)')]

    def __init__(self, name=None, **kwarg):
        super(YelpSpider, self).__init__(name, **kwarg)

    def get_callback(self, link):
        return self.parse_item if _matches(link, self.item_regexs) else self.parse

    def get_rule_list(self):
        return [
            {
                'allow': r'^http://www.yelp.com/biz/+(\w*)',
                'process_links': 'process_links',
                'check_url': True,
            },
            {
                'allow': r'^http://www.yelp.com/search\?cflt=restaurants&find_desc=&find_loc=+(.*)&start=+(.*)',
                'process_links': 'process_links',
                'check_url': True,
                'link_type': LinkType.CATELOG,
            },
        ]


class TripAdvisorSpider(AppSpider):

    name = "tripadvisor.com"
    itemloader_class = TripAdvisorItemLoader
#    scriptprocessor_class = TripAdvisorScriptProcessor
    item_regexs = [re.compile(r'^http://www.tripadvisor.com/Hotel_Review+(.*).html')]

    def __init__(self, name=None, **kwarg):
        super(TripAdvisorSpider, self).__init__(name, **kwarg)

    def get_callback(self, link):
        return self.parse_item if _matches(link, self.item_regexs) else self.parse

    def get_rule_list(self):
        return [
            {
                'allow': r'^http://www.tripadvisor.com/Hotel_Review+(.*).html',
                'check_url': True,
            },
            {
                'allow': r'^http://www.tripadvisor.com/Hotels+(.*).html',
                'process_links': 'process_links',
                'check_url': True,
                'link_type': LinkType.CATELOG,
            },
            {
                'allow': r'^http://www.tripadvisor.com/Tourism+(.*).html',
                'process_links': 'process_links',
                'check_url': True,
                'link_type': LinkType.CATELOG,
            },
        ]


class AppleSpider(AppSpider):

    name = "itunes.apple.com"
    itemloader_class = AppleItemLoader
#    item_regexs = [re.compile(r'^http://itunes.apple.com/us/app/(.*)/id+(.*)\?mt=8')]
    item_regexs = [re.compile(r'^https://itunes.apple.com/cn/app/(.*)/id+(.*)\?mt=8')]

    def __init__(self, name=None, **kwarg):
        super(AppleSpider, self).__init__(name, **kwarg)

    def get_callback(self, link):
        return self.parse_item if _matches(link, self.item_regexs) else self.parse

    def get_rule_list(self):
        return [
            {
                'allow': r'^https://itunes.apple.com/cn/app/(.*)/id+(.*)\?mt=8',
                'check_url': True,
            },
            #                    {
            #                     'allow': r'^https://itunes.apple.com/cn/genre/ios(.*)/id(.*)\?mt=8(.*)',
            #                     'check_url': True,
            #                     'link_type': LinkType.CATELOG,
            #                    },
            {
                'allow': r'^https://itunes.apple.com/cn/genre/ios(.*)/id(.*)\?mt=8$',
                'check_url': True,
                'link_type': LinkType.CATELOG,
            },
        ]


class WandoujiaSpider(AppSpider):

    name = "wandoujia.com"
    itemloader_class = WandoujiaItemLoader
    item_regexs = [re.compile(r'^http://www.wandoujia.com/apps/(.*)\.(.*)')]
    item_zhushou_regexs = [re.compile('^http://apps.wandoujia.com/api/.*')]

    def __init__(self, name=None, **kwarg):
        super(WandoujiaSpider, self).__init__(name, **kwarg)

    def get_callback(self, link):
        if _matches(link, self.item_regexs):
            return self.parse_item
        elif _matches(link, self.item_zhushou_regexs):
            return self.parse_zhushou_cate
        else:
            return self.parse

    def parse_zhushou_cate(self, response):
        meta = response.request.meta
        source = meta['domain']
        url = response.request.url
        import simplejson
        data = simplejson.loads(response.body)
        pns = jsonutils.find_attr(data, 'packageName', str)
        urls = ['http://www.wandoujia.com/apps/%s' % pn for pn in pns]

        if urls:
            if self.name.startswith('update.'):
                service.report_update_status([LinkStatus(u, source, Status.FOUND, LinkType.LEAF) for u in urls])
                service.report_update_status([LinkStatus(url, source, Status.SUCCEED, LinkType.CATELOG, len(urls))])
            else:
                service.report_status([LinkStatus(u, source, Status.FOUND, LinkType.LEAF) for u in urls])
                service.report_status([LinkStatus(url, source, Status.SUCCEED, LinkType.CATELOG, len(urls))])

    def get_rule_list(self):
        return [
            {
                'allow': r'^http://www.wandoujia.com/apps/[a-zA-Z0-9]*\.(.*)',
                'check_url': True,
            },
            {
                'allow': r'^^http://www.wandoujia.com/apps/[a-z]*',
                'check_url': True,
                'link_type': LinkType.CATELOG,
            },
        ]


class UpdateWandoujiaSpider(WandoujiaSpider):

    name = "update.wandoujia.com"

    def __init__(self, name=None, **kwarg):
        super(UpdateWandoujiaSpider, self).__init__(name, **kwarg)

    def get_rule_list(self):
        return [
            {
                'allow': r'^http://www.wandoujia.com/apps/[a-zA-Z0-9]*\.(.*)',
                'check_url': True,
            },
        ]


class UpdateMyAppSpider(AppSpider):

    name = "update.myapp.com"
    itemloader_class = MyAppItemLoader
    item_regexs = [re.compile(r'^http://android.myapp.com/android/appdetail.jsp')]
    category_api_regexs = [re.compile(r'^http://android.myapp.com/android/qrycategoryranking_web')]
    related_api_regexs = [re.compile(r'^http://android.myapp.com/android/qryrelatesoft_web')]

    def __init__(self, name=None, **kwarg):
        super(UpdateMyAppSpider, self).__init__(name, **kwarg)

    def get_callback(self, link):
        if _matches(link, self.item_regexs):
            return self.parse_item
        elif _matches(link, self.category_api_regexs) or _matches(link, self.related_api_regexs):
            return self.parse_api
        else:
            return self.parse

    def get_rule_list(self):
        return [
            {
                'allow': r'^http://android.myapp.com/android/appdetail.jsp',
                'check_url': True,
            },
        ]

    def parse_api(self, response):
        meta = response.request.meta
        source = meta['domain']
        all_link = []
        url = response.request.url

        json_data = json.loads(response.body)

        for v in json_data['info']['value']:
            aid = v['appid']
            link = "http://android.myapp.com/android/appdetail.jsp?appid=%s" % aid
            if link not in all_link:
                if url.find('qryrelate') == -1:
                    related_api = 'http://android.myapp.com/android/qryrelatesoft_web?appid=%s&icontype=60&pageNo=1&pageSize=50' % aid
                    all_link.append(related_api)
                all_link.append(link)

        if all_link:
            if self.name.startswith('update.'):
                service.report_update_status([LinkStatus(link, source, Status.FOUND, LinkType.CATELOG)
                                             for link in all_link])
                service.report_update_status([LinkStatus(url, source, Status.SUCCEED, LinkType.CATELOG, len(all_link))])
            else:
                service.report_status([LinkStatus(link, source, Status.FOUND, LinkType.CATELOG) for link in all_link])
                service.report_status([LinkStatus(url, source, Status.SUCCEED, LinkType.CATELOG, len(all_link))])

    """
    def start_requests(self):
        for link in ('http://android.myapp.com/android/appdetail.jsp?appid=608583',):
            yield self._create_request(link)
    """


class DownloadLinkSpider(CrawlSpider):
    name = 'downloadlink.as.baidu.com'
    allowed_domains = ['shouji.baidu.com']
    #redirectprocessor_class = RedirectShoujiBaiduProcessor
    #redirectprocessor_class = None
    #redirectprocessor_class = ThreeGRedirectProcessor

    def build_rules(self):
        rules = [
            #{
            #    'allow': [r'^http://as.baidu.com/a/item\?docid=.*$', ],
            #    'allow_domains': ['as.baidu.com',],
            #    'callback': 'parse_item',
            #},
            #{
            #    'allow': [r'^http://as.baidu.com/a/rank\?.*$', ],
            #    'allow_domains': ['as.baidu.com',],
            #},
            {
                'allow': [r'^http://shouji.baidu.com/software/list\?cid=.*$',
                          r'^http://shouji.baidu.com/game/list\?cid=.*$',],
                'allow_domains': [r'shouji.baidu.com',],
            },
            {
                'allow': [r'^http://shouji.baidu.com/game/item\?docid=.*$',
                          r'^http://shouji.baidu.com/soft/item\?docid=.*$',
                          r'^http://shouji.baidu.com/software/item\?docid=.*$',],
                          #r'^http://shouji.baidu.com/game/item\?bdtype=game&docid=.*$',
                          #r'^http://shouji.baidu.com/soft/item\?bdtype=soft&docid=.*$',
                          #r'^http://shouji.baidu.com/software/item\?bdtype=soft&docid=.*$', ],
                #'allow': [r'^http://shouji.baidu.com/game/item\?.*$', ],
                'allow_domains': ['shouji.baidu.com', ],
                'callback': 'parse_zhushou_item',
            },
        ]
        self.rules = []
        for rule in rules:
            if 'callback' in rule:
                callback = rule.pop('callback')
            else:
                callback = None
            self.rules.append(Rule(SgmlLinkExtractor(**rule), callback=callback))

    def __init__(self, *a, **kw):
        self.build_rules()
        CrawlSpider.__init__(self, *a, **kw)
        start_urls = [
            #'http://as.baidu.com/a/software?cid=101&s=1&pn=%d',
            #'http://as.baidu.com/a/asgame?cid=102&s=1&pn=%d',
            #'http://as.baidu.com/a/software?cid=101&s=2&pn=%d',
            #'http://as.baidu.com/a/asgame?cid=102&s=2&pn=%d',
            'http://shouji.baidu.com/software/list?cid=501&page_num=%d',  # soft->system tools
            'http://shouji.baidu.com/software/list?cid=502&page_num=%d',  # soft->desk top
            'http://shouji.baidu.com/software/list?cid=503&page_num=%d',  # soft->socail communication
            'http://shouji.baidu.com/software/list?cid=508&page_num=%d',  # soft->photo process 
            'http://shouji.baidu.com/software/list?cid=506&page_num=%d',  # soft->multimedia player
            'http://shouji.baidu.com/software/list?cid=504&page_num=%d',  # soft->life application
            'http://shouji.baidu.com/software/list?cid=510&page_num=%d',  # soft->shopping
            'http://shouji.baidu.com/software/list?cid=507&page_num=%d',  # soft->study and work
            'http://shouji.baidu.com/software/list?cid=505&page_num=%d',  # soft->reading and news
            'http://shouji.baidu.com/software/list?cid=509&page_num=%d',  # soft->travel and journey
        
            'http://shouji.baidu.com/game/list?cid=401&page_num=%d',  # game->puz
            'http://shouji.baidu.com/game/list?cid=401&page_num=%d',  # game->puz
            
            'http://shouji.baidu.com/game/list?cid=402&page_num=%d',  # game->rpg
            'http://shouji.baidu.com/game/list?cid=403&page_num=%d',  # game->fps
            'http://shouji.baidu.com/game/list?cid=404&page_num=%d',  # game->edu
            'http://shouji.baidu.com/game/list?cid=405&page_num=%d',  # game->spt
            'http://shouji.baidu.com/game/list?cid=406&page_num=%d',  # game->rac
            'http://shouji.baidu.com/game/list?cid=407&page_num=%d',  # game->avg
            'http://shouji.baidu.com/game/list?cid=408&page_num=%d',  # game->spg
        ]

        #new_start_urls = [
        #    'http://shouji.baidu.com/game/list?cid=102&from=pcsuite&board_type=tophot&bdtype=game&page_num=%d',
        #    'http://shouji.baidu.com/software/list?cid=101&from=pcsuite&board_type=tophot&bdtype=soft&page_num=%d',
        #]
        self.start_urls = []
        for u in start_urls:
            for i in range(0, 5):
                self.start_urls.append(u % i)

        #for u in new_start_urls:
        #    for i in range(1, 50):
        #        self.start_urls.append(u % i)
        self.start_urls.append('http://as.baidu.com/a/rank')
        log_info(self.start_urls)

    def parse_item(self, response):
        sel = HtmlXPathSelector(response)
        urls = sel.select('//div[@class="origin-wrap"]/ul/li/a/@data-ajaxurl').extract()
        for u in urls:
            # yield Request(url=u, callback=self.parse_item_link)
            yield Request(url=u, callback=self.parse_item_link_v2)

    def parse_item_link(self, response):
        try:
            json = simplejson.loads(response.body)
            url = json.get('downloadUrl', None)
            if url:
                print 'crawled url: %s' % url
                yield DownloadLinkItem(url=url)
        except Exception as e:
            log_error('parse json failed for string: %s' % response.body)

    def parse_item_link_v2(self, response):
        url = None
        try:
            json = simplejson.loads(response.body)
            url = json.get('downloadUrl', None)
        except Exception as e:
            log_error('parse json failed for string: %s' % response.body)
            begin_tag_string = "\"downloadUrl\":\""
            end_tag_string = "\",\""
            begin_tag_index = response.body.find(begin_tag_string)
            if begin_tag_index != -1:
                end_tag_index = response.body[begin_tag_index:].find(end_tag_string)
                if end_tag_index != -1:
                    url = response.body[begin_tag_index + len(begin_tag_string) : begin_tag_index + end_tag_index]
                    log_info('parse json error rectified! url=%s' % url)
            else:
                log_error('try find downloadUrl form the broken jsonstring above failed!')
        if url:
            print 'crawled url: %s' % url
            yield DownloadLinkItem(url=url)    

    
    def parse_zhushou_item(self, response):
        log_info("OK! new active!!!!!!!!!!!!!!!")
        sel = HtmlXPathSelector(response)
        urls = sel.select('//div[@class="area-download"]/a[@class="apk"]/@href').extract()
        #urls = sel.select('//div[@class="intro yui3-u"]/a[@class="inst-btn-big custom-btn-big"]/@data_url').extract()
        if len(urls) != 1:
          log_warning('can not find valid download link!')
        else:
          log_info("crawled url: %s" % urls[0])
          print 'crawled url: %s' % urls[0]
          yield DownloadLinkItem(url=urls[0])    

