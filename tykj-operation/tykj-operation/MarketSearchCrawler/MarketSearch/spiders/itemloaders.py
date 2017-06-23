# coding=UTF-8
'''
Created on May 26, 2011

@author: yan
'''

from scrapy.contrib.loader import XPathItemLoader, ItemLoader
from MarketSearch.items import AppItem, FinalAppItem
from MarketSearch.items import AppleItem
from MarketSearch.items import YelpItem
from MarketSearch.items import YoutubeItem
from MarketSearch.items import TripAdvisorItem
from MarketSearch.utils import log_error, log_info, log_warning
import string

import sys
import urllib2
import traceback
import re
import requests
import datetime
from datetime import datetime as _datetime
import time
reload(sys)
sys.setdefaultencoding("utf-8")


class XiaomiThemeItemLoader(XPathItemLoader):

    def __init__(self, selector):
        self._selector = selector
        super(XiaomiThemeItemLoader, self).__init__(item=AppItem(), selector=self._selector)
        self._init_path()

    def _init_path(self):
        self.add_xpath('name', '//div[@class="mod detail"]/div/h2/text()')
        self.add_xpath('icon_link', '//div[@id="J_detail"]//img[1]/@src')
        self.add_xpath('rating', '//div[@id="commentRankPoint"]/@class')
        self.add_xpath('version', '//div[@class="mod detail-infos"]/div[@class="bd"]/div/text()')
#        self.add_xpath('developer', '//label[@id="ctl00_AndroidMaster_Content_Apk_SoftDeveloper"]/text()')
#        self.add_xpath('sdk_support', '//label[@id="ctl00_AndroidMaster_Content_Apk_SoftSuitSdk"]/text()')
        self.add_xpath('category', '//div[@class="mod theme-nav"]/div[@class="bd"]/a[@class="selected"]/b/text()')
#        self.add_xpath('screen_support', '//label[@id="ctl00_AndroidMaster_Content_Apk_SupportScreen"]/text()')
#        self.add_xpath('apk_size', '//label[@id="ctl00_AndroidMaster_Content_Apk_SoftSize"]/text()')
#        self.add_xpath('language', '//label[@id="ctl00_AndroidMaster_Content_Apk_SoftLanguage"]/text()')
#        self.add_xpath('publish_date', '//label[@id="ctl00_AndroidMaster_Content_Apk_SoftPublishTime"]/text()')
#        self.add_xpath('downloads', '//label[@id="ctl00_AndroidMaster_Content_Apk_Download"]/text()')
        self.add_xpath('description', '//div[@class="mod userinfos"]/div[@class="bd"]/node()')
        self.add_xpath('images', '//div[@id="J_detail"]//img/@src')
        #self.add_xpath('update_date', '//label[@id="Apk_SoftUpdateTime"]/text()')
        #self.add_xpath('update_description', '//label[@id="Apk_SoftUpdateDescription"]/text()')
#        self.add_xpath('qr_link', '//input[@id="hiQRCode"]/@value')
        self.add_xpath('download_link', '//div[@id="J-downWrap"]/a[@class="download-pc J_Download"]/@href')


class QihuItemLoader(XPathItemLoader):

    def __init__(self, selector):
        self._selector = selector
        super(QihuItemLoader, self).__init__(item=AppItem(), selector=self._selector)
        self._init_path()

    def _init_path(self):
        self.add_xpath('name', '//dl[@class="clearfix"]/dd/h3/text()')
        self.add_xpath('icon_link', '//dl[@class="clearfix"]/dt/img/@src')
        self.add_xpath('rating', '//dl[@class="clearfix"]/dd[2]/em/text()')
        self.add_xpath('publish_date', '//dl[@class="clearfix"]/dd[2]/p[3]/text()')
        self.add_xpath('downloads', '//dl[@class="clearfix"]/dd[2]/p[2]/text()')
        self.add_xpath('description', '//div[@class="alldesc"]')
        self.add_xpath('screen_support', '//div[@class="nstxt"]/table/node()')
        self.add_xpath('images', '//div[@class="overview"]//img/@src')
        self.add_xpath('download_link', '//script[1]/text()')


class OneMobileAPIItemLoader(ItemLoader):

    def __init__(self, item=None, **context):
        ItemLoader.__init__(self, item=item, **context)

    def add_value(self, field_name, value, *processors, **kw):
        return ItemLoader.add_value(self, field_name, value, *processors, **kw)


class GooglePlayItemLoader(XPathItemLoader):

    def __init__(self, selector=None, response=None, **context):
        self._selector = selector
        XPathItemLoader.__init__(self, item=FinalAppItem(), selector=self._selector, response=response, **context)
        self._init_path()

    def _init_path(self):
        xpath_dict = {
            'name': '//div[@class="details-info"]/div[@class="info-container"]/div/div/text()',
            'icon_link': '//div[@class="details-info"]/div[@class="cover-container"]/img/@src',
            'rating': '//div[@class="score"]/text()',
            'version': '//div[@class="details-wrapper"]//div[@itemprop="softwareVersion"]/text()',
            'developer': '//div[@class="details-info"]//div[@itemprop="author"]/a/text()',
            'sdk_support': '//div[@class="details-wrapper"]//div[@itemprop="operatingSystems"]/text()',
            'category': '//div[@class="details-info"]//a[@class="document-subtitle category"]/span/text()',
            'screen_support': '/xxxxxxxxxxxxxxxxxx',
            'apk_size': '//div[@class="details-wrapper"]//div[@itemprop="fileSize"]/text()',
            'publish_date': '//div[@class="details-wrapper"]//div[@itemprop="datePublished"]/text()',
            'downloads': '//div[@class="details-wrapper"]//div[@itemprop="numDownloads"]/text()',
            'description': '//div[@itemprop="description"]//text()',
            'images': '//img[@itemprop="screenshot"]/@src',
        }
        for k, v in xpath_dict.items():
            self.add_xpath(k, v)
        response = self.context['response']
        url = response.request.url
        params = dict([p.split('=') if len(p.split('=')) == 2 else (p, '') for p in url[url.find('?') + 1:].split('&')])
        self.add_value('package_name', params['id'])
        description = self.get_xpath('//div[@class="doc-whatsnew-container"]//*//text()')
        if description == [u'\u6700\u8fd1\u6ca1\u6709\u66f4\u6539\u3002'] or \
           description == [u'\u6700\u8fd1\u6c92\u6709\u8b8a\u66f4\u3002']:
            description = self.get_xpath('//div[@id="doc-original-text"]/node()')
        else:
            description = self.get_xpath('//div[@id="doc-original-text"]/node()') + \
                self.get_xpath('//div[@class="doc-whatsnew-container"]/node()')
            description = string.join(description)
        self.add_value('description', description)  # a piece html fragment
        self._add_defaults()

    def _add_defaults(self):
        defaults_dict = {
            'screen_support': '',
            'language': '',
            'qr_link': '',
            'download_link': '',
            'update_note': '',
            'avail_download_links': '',
            'error': '',
            'labels': '',
            'sig': '',
            'tag': '',
            'package_hash': '',
            'min_sdk_version': 0,
            'version_code': 0,
            'vol_id': 0,
            'file_type': 'apk',
            'is_break': -1,
            'platform': 1,
            'status': 0,
            'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        for k, v in defaults_dict.items():
            self.add_value(k, v)


class OneMobileItemLoader(XPathItemLoader):

    def __init__(self, selector):
        self._selector = selector
        XPathItemLoader.__init__(self, item=AppItem(), selector=self._selector)
        self._init_path()

    def _init_path(self):
        xpath_dict = {
            'name': "//div[@class='detailinfo']/div[@class='detailitem mb10']/h1[@class='apptitle']/text()",
            'icon_link': "//div[@class='side']/div[@class='appdown']/div[@class='pic']/img/@src",
            'publish_date': "//div[@class='side']/div[@class='appinfo']/dl/dd[3]/text()",
            'category': "//div[@class='side']/div[@class='appinfo']/dl/dd[2]/a/text()",
            'downloads': "//div[@class='side']/div[@class='appinfo']/dl/dd[@class='num']/text()",
            'description':
            "//div[@class='detailinfo']/div[@class='detailitem mb10']/div[@id='baseinfo']/div[@class='allinfo']/text()",
            'images': "//div[@class='detailinfo']//div[@class='detailsliderviewport']//span/a/img/@src",
            'developer': "//div[@class='side']/div[@class='appinfo']/dl/dd[1]/text()",
            'version': "//div[@class='side']/div[@class='appinfo']/dl/dd[4]/text()",
        }
        for k, v in xpath_dict.items():
            self.add_xpath(k, v)
        downloads = self.get_xpath("//div[@class='side']/div[@class='appdown']//a[@class='btninstall']/@onclick")
        r = re.compile("downloadurl\('([^'\)]+)',.*")
        m = r.match(downloads[0])
        url = 'http://www.1mobile.com/d.php?pkg=%s' % m.groups()[0]
        self.add_value('download_link', requests.get(url).content)


class BaiduItemLoader(XPathItemLoader):

    def __init__(self, selector):
        self._selector = selector
        super(BaiduItemLoader, self).__init__(item=AppItem(), selector=self._selector)
        self._init_path()

    def _init_path(self):
        self.add_xpath('name', '//span[@id="appname"]/text()')
        self.add_xpath('icon_link', '//img[@id="app-logo"]/@src')
        self.add_xpath('rating', '//b[@id="score-num"]/text()')
        version1 = self.get_xpath('//span[@class="params-vname"]/text()')
        version2 = self.get_xpath('//span[@id="params-vname"]/text()')
        if version1:
            self.add_value('version', version1)
        else:
            self.add_value('version', version2)
        # use developer save source market
        developer1 = self.get_xpath('//span[@id="target-origin"]/text()')
        developer2 = self.get_xpath('//a[@class="origin-target"]/text()')
        if developer1:
            self.add_value('developer', developer1)
        else:
            self.add_value('developer', developer2)
        self.add_xpath('sdk_support', '//span[@class="params-platform"]/text()')
        category1 = self.get_xpath('//span[@id="params-catename"]/text()')
        category2 = self.get_xpath('//span[@class="params-catename"]/text()')
        if category1:
            self.add_value('category', category1)
        else:
            self.add_value('category', category2)
#        self.add_xpath('screen_support', '//div[@class="soft_detail_subsInfo"]/p/node()')
        self.add_xpath('apk_size', '//span[@class="params-size"]/text()')
        # use language save baidu docid
        self.add_xpath('language', '//input[@id="sendmsg_docid"]/@value')
        self.add_xpath('publish_date', '//span[@class="params-updatetime"]/text()')
#        self.add_xpath('downloads', '//label[@id="ctl00_AndroidMaster_Content_Apk_Download"]/text()')
        self.add_xpath('description', '//div[@class="brief-des"]')
        self.add_xpath('images', '//ul[@class="screen cls data-screenshots"]//img/@src')

        labels = self.get_xpath('//table[@class="safety-data-table"]//tr/td[2]/a/text()')
        official = self.get_xpath('//span[@class="official"]')
        ad = self.get_xpath('//span[@class="ad_icon"][@style="display:inline-block"]')
        energe = self.get_xpath('//span[@class="energe_icon"][@style="display:inline-block"]')
        if ad:
            labels.append(u'内置广告')
        self.add_value('labels', ','.join(labels))
        self.add_xpath('download_link', '//a[@class="bd-download event-apk-download tjitem"]/@href')


class ShoujiBaiduItemLoader(XPathItemLoader):
    def __init__(self, selector):
        self._selector = selector
        super(ShoujiBaiduItemLoader, self).__init__(item=AppItem(), selector=self._selector)
        self._init_path()

    def _init_path(self):
        self.add_xpath('name', '//div[@class="intro-top"]//h1[@class="app-name"]/span/text()')
        self.add_xpath('icon_link', '//div[@class="intro-top"]//div[@class="app-pic"]/img/@src')
        rating_strs = self.get_xpath('//span[@class="star-percent"]/@style')
        try:
            rating_value = int(rating_strs[0].strip('%').split(':')[1]) * 5 / 100
        except Exception as e:
            log_info('get no ratting for baidu app! default to 0 %s' % e)
            rating_value = 0
     
        self.add_value('rating', str(rating_value) + ' ')
        #self.add_xpath('rating', '//span[@class="star-percent"]/@style')
        version1 = self.get_xpath('//div[@class="area-download"]/a[1]/@data_versionname')
        # version2 = self.get_xpath('//span[@id="params-vname"]/text()')
        #if version1:
        self.add_value('version', version1)
        # else:
        #    self.add_value('version', version2)
        # use developer save source market
        developer1 = self.get_xpath('//div[@class="origin-wrap"]/a[@class="origin"]/text()')
        developer2 = self.get_xpath('//div[@class="origin-wrap"]//span[@class="gold"]/following-sibling::span[1]/text()')
        if developer1:
            self.add_value('developer', developer1)
        else:
            self.add_value('developer', developer2)
        ## self.add_xpath('sdk_support', '//span[@class="params-platform"]/text()')
        self.add_value('sdk_support', '')
        category1 = self.get_xpath('//div[@class="nav"]/span[1]/a/text()')
        category2 = self.get_xpath('//div[@class="nav"]/span[3]/a/text()')
        if category1:
            self.add_value('category', category1)
        else:
            self.add_value('category', category2)
#        self.add_xpath('screen_support', '//div[@class="soft_detail_subsInfo"]/p/node()')
        self.add_xpath('apk_size', '//div[@class="area-download"]/a[1]/@data_size')
        # use language save baidu docid
        self.add_xpath('language', '//input[@id="sendmsg_docid"]/@value')
        # self.add_xpath('publish_date', '//span[@class="params-updatetime"]/text()')
        self.add_value('publish_date', _datetime.today().strftime("%Y-%m-%d") ) # fake. 
#        self.add_xpath('downloads', '//label[@id="ctl00_AndroidMaster_Content_Apk_Download"]/text()')
        self.add_xpath('description', '//div[@class="brief-short"]/p/text()')
        self.add_xpath('images', '//div[@class="screenshot-container screenshots-container"]//ul/li/img/@src')

        labels = self.get_xpath('//span[@class="app-feature-detail"]/span/text()')
        official = self.get_xpath('//span[@class="official"]')
        ad = self.get_xpath('//span[@class="ad_icon"][@style="display:inline-block"]')
        energe = self.get_xpath('//span[@class="energe_icon"][@style="display:inline-block"]')
        if ad:
            labels.append(u'内置广告')
        self.add_value('labels', ','.join(labels))
        self.add_xpath('download_link', '//div[@class="area-download"]/a[1]/@data_url')


class NewShoujiBaiduItemLoader(XPathItemLoader):
    def __init__(self, selector):
        self._selector = selector
        super(NewShoujiBaiduItemLoader, self).__init__(item=AppItem(), selector=self._selector)
        self._init_path()

    def _init_path(self):
        self.add_xpath('name', '//div[@class="intro yui3-u"]/a[@class="inst-btn-big custom-btn-big"]/@data_name')
        self.add_xpath('icon_link', '//div[@class="intro yui3-u"]/a[@class="inst-btn-big custom-btn-big"]/@data_icon')
        rating_strs = self.get_xpath('//span[@class="star-percent"]/@style')
        try:
            rating_value = int(rating_strs[0].strip(';').strip('%').split(':')[1]) * 5 / 100
        except Exception as e:
            log_info('get no ratting for baidu app! default to 0 %s' % e)
            rating_value = 0
     
        self.add_value('rating', str(rating_value) + ' ')
        #self.add_xpath('rating', '//span[@class="star-percent"]/@style')
        version1 = self.get_xpath('//div[@class="intro yui3-u"]/a[@class="inst-btn-big custom-btn-big"]/@data_versionname')
        # version2 = self.get_xpath('//span[@id="params-vname"]/text()')
        #if version1:
        self.add_value('version', version1)
        # else:
        #    self.add_value('version', version2)
        # use developer save source market
        developer1 = self.get_xpath('//a[@class="origin"]/text()')
        developer2 = self.get_xpath('//div[@class="origin-wrap"]//span[@class="gold"]/following-sibling::span[1]/text()')
        if developer1:
            self.add_value('developer', developer1)
        else:
            self.add_value('developer', developer2)
        ## self.add_xpath('sdk_support', '//span[@class="params-platform"]/text()')
        self.add_xpath('sdk_support', '//tr[@class="hideparam"]/td[2]/text()')
        category1 = self.get_xpath('//div[@class="nav"]/span[1]/a/text()')
        category2 = self.get_xpath('//div[@class="nav"]/span[3]/a/text()')
        if category1:
            self.add_value('category', category1)
        else:
            self.add_value('category', category2)
#        self.add_xpath('screen_support', '//div[@class="soft_detail_subsInfo"]/p/node()')
        self.add_xpath('apk_size', '//div[@class="intro yui3-u"]/a[@class="inst-btn-big custom-btn-big"]/@data_size')
        # use language save baidu docid
        self.add_xpath('language', '//input[@id="sendmsg_docid"]/@value')
        ## self.add_xpath('publish_date', '//span[@class="params-updatetime"]/text()')
        publish_date_tags = self.get_xpath('//tr[@class="hideparam"]/td[1]/text()')
        # self.add_xpath('publish_date', '//span[@class="params-updatetime"]/text()')
        publish_info = '0'
        try:
            log_info("=================== publish_date=%s*******" % str(publish_date_tags))
            date_str = publish_date_tags[0].split(':')[1].strip(' ')
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            utc_timestamp = time.mktime(date_obj.timetuple())
            publish_info = str(utc_timestamp)
        except Exception as e:
            log_info('get no publish date for baidu app! err=%s' % e)
        self.add_value('publish_date', publish_info)

#        self.add_xpath('downloads', '//label[@id="ctl00_AndroidMaster_Content_Apk_Download"]/text()')
        self.add_xpath('description', '//div[@class="brief-short"]/p/text()')
        self.add_xpath('images', '//div[@class="picsinner"]/img/@src')

        #labels = self.get_xpath('//span[@class="app-feature-detail"]/span/text()')
        #official = self.get_xpath('//span[@class="official"]')
        #ad = self.get_xpath('//span[@class="ad_icon"][@style="display:inline-block"]')
        #energe = self.get_xpath('//span[@class="energe_icon"][@style="display:inline-block"]')
        labels = self.get_xpath('//span[@class="guanfang custom-tag"]/text()')       
 
        #if ad:
        #    labels.append(u'内置广告')
        self.add_value('labels', ','.join(labels))
        self.add_xpath('download_link', '//div[@class="intro yui3-u"]/a[@class="inst-btn-big custom-btn-big"]/@data_url')

class NineOneIphoneItemLoader(XPathItemLoader):

    def __init__(self, selector):
        self._selector = selector
        super(NineOneIphoneItemLoader, self).__init__(item=AppItem(), selector=self._selector)
        self._init_path()

    def _init_path(self):
        self.add_xpath('name', '//div[@class="soft_detail_h3"]/h3/text()')
        self.add_xpath('icon_link', '//div[@class="soft_detail_img"]/p/a/img[1]/@src')
        self.add_xpath('rating', '//div[@class="xingjituijian"]/script/text()')
        self.add_xpath('version', '//div[@class="soft_detail_h3"]/span/text()')
#        self.add_xpath('developer', '//label[@id="ctl00_AndroidMaster_Content_Apk_SoftDeveloper"]/text()')
#        self.add_xpath('sdk_support', '//label[@id="ctl00_AndroidMaster_Content_Apk_SoftSuitSdk"]/text()')
        self.add_xpath('category', '//div[@class="soft_title"]/h2/a[2]/text()')
        self.add_xpath('screen_support', '//div[@class="soft_detail_subsInfo"]/p')
#        self.add_xpath('apk_size', '//label[@id="ctl00_AndroidMaster_Content_Apk_SoftSize"]/text()')
#        self.add_xpath('language', '//label[@id="ctl00_AndroidMaster_Content_Apk_SoftLanguage"]/text()')
#        self.add_xpath('publish_date', '//label[@id="ctl00_AndroidMaster_Content_Apk_SoftPublishTime"]/text()')
#        self.add_xpath('downloads', '//label[@id="ctl00_AndroidMaster_Content_Apk_Download"]/text()')
        self.add_xpath('description', '//div[@class="soft_detail_info"]/div[3]/node()')
        self.add_xpath('images', '//div[@class="soft_detail_pic"]/script/text()')
        #self.add_xpath('update_date', '//label[@id="Apk_SoftUpdateTime"]/text()')
#        self.add_xpath('update_description', '//div[@class="soft_detail_subsInfo"]/node()')
#        self.add_xpath('qr_link', '//div[@class="soft_detail_subsInfo"]/node()')
        self.add_xpath('download_link', '//a[@class="comment_up"]/@href')


class NineOneItemLoader(XPathItemLoader):

    def __init__(self, selector):
        self._selector = selector
        super(NineOneItemLoader, self).__init__(item=AppItem(), selector=self._selector)
        self._init_path()

    def _init_path(self):
        self.add_xpath('name', '//div[@class="theme_detail_r"]/h2/text()')
        self.add_xpath('icon_link', '//p[@id="theme_detail_fbc"]/a/img/@src')
        self.add_xpath('rating', '//div[@class="theme_detail_r"]/script/text()')
#        self.add_xpath('version', '//div[@class="theme_detail_r"]/p/node()')
#        self.add_xpath('developer', '//label[@id="ctl00_AndroidMaster_Content_Apk_SoftDeveloper"]/text()')
#        self.add_xpath('sdk_support', '//label[@id="ctl00_AndroidMaster_Content_Apk_SoftSuitSdk"]/text()')
#        self.add_xpath('category', '//div[@class="theme_detail_r"]/p/node()')
#        self.add_xpath('screen_support', '//label[@id="ctl00_AndroidMaster_Content_Apk_SupportScreen"]/text()')
#        self.add_xpath('apk_size', '//label[@id="ctl00_AndroidMaster_Content_Apk_SoftSize"]/text()')
#        self.add_xpath('language', '//label[@id="ctl00_AndroidMaster_Content_Apk_SoftLanguage"]/text()')
#        self.add_xpath('publish_date', '//label[@id="ctl00_AndroidMaster_Content_Apk_SoftPublishTime"]/text()')
#        self.add_xpath('downloads', '//label[@id="ctl00_AndroidMaster_Content_Apk_Download"]/text()')
        self.add_xpath('description', '//div[@class="theme_detail_r"]/p/node()')
        self.add_xpath('images', '//p[@id="theme_detail_fbc"]/a/img/@src')
        #self.add_xpath('update_date', '//label[@id="Apk_SoftUpdateTime"]/text()')
        #self.add_xpath('update_description', '//label[@id="Apk_SoftUpdateDescription"]/text()')
#        self.add_xpath('qr_link', '//input[@id="hiQRCode"]/@value')
        self.add_xpath('download_link', '//div[@class="theme_detail_btn"]/a[1]/@href')


class NineOneImageItemLoader(XPathItemLoader):

    def __init__(self, selector):
        self._selector = selector
        super(NineOneImageItemLoader, self).__init__(item=AppItem(), selector=self._selector)
        self._init_path()

    def _init_path(self):
        self.add_xpath('name', '//div[@class="pic_detail_r"]/h2/text()')
        self.add_xpath('icon_link', '//p[@id="pic_detail_fbc"]/a/img/@src')
        self.add_xpath('rating', '//div[@class="pic_detail_r"]/script/text()')
#        self.add_xpath('version', '//div[@class="pic_detail_r"]/p/node()')
#        self.add_xpath('developer', '//label[@id="ctl00_AndroidMaster_Content_Apk_SoftDeveloper"]/text()')
#        self.add_xpath('sdk_support', '//label[@id="ctl00_AndroidMaster_Content_Apk_SoftSuitSdk"]/text()')
#        self.add_xpath('category', '//div[@class="pic_detail_r"]/p/node()')
#        self.add_xpath('screen_support', '//label[@id="ctl00_AndroidMaster_Content_Apk_SupportScreen"]/text()')
#        self.add_xpath('apk_size', '//label[@id="ctl00_AndroidMaster_Content_Apk_SoftSize"]/text()')
#        self.add_xpath('language', '//label[@id="ctl00_AndroidMaster_Content_Apk_SoftLanguage"]/text()')
#        self.add_xpath('publish_date', '//label[@id="ctl00_AndroidMaster_Content_Apk_SoftPublishTime"]/text()')
#        self.add_xpath('downloads', '//label[@id="ctl00_AndroidMaster_Content_Apk_Download"]/text()')
        self.add_xpath('description', '//div[@class="pic_detail_r"]/p/node()')
        self.add_xpath('images', '//p[@id="pic_detail_fbc"]/a/img/@src')
        #self.add_xpath('update_date', '//label[@id="Apk_SoftUpdateTime"]/text()')
        #self.add_xpath('update_description', '//label[@id="Apk_SoftUpdateDescription"]/text()')
#        self.add_xpath('qr_link', '//input[@id="hiQRCode"]/@value')
        self.add_xpath('download_link', '//div[@class="pic_detail_btn"]/a[1]/@href')


class HiApkItemLoader(XPathItemLoader):

    def __init__(self, selector):
        self._selector = selector
        super(HiApkItemLoader, self).__init__(item=AppItem(), selector=self._selector)
        self._init_path()

    def _init_path(self):
        self.add_xpath('name', '//label[@id="ctl00_AndroidMaster_Content_Apk_SoftName"]/text()')
        self.add_xpath('icon_link', '//div[@class="detail_content"]/div[1]/div/img/@src')
        self.add_xpath('rating', '//div[@class="star_num"]/text()')
        self.add_xpath('version', '//label[@id="ctl00_AndroidMaster_Content_Apk_SoftVersionName"]/text()')
        self.add_xpath('developer', '//label[@id="ctl00_AndroidMaster_Content_Apk_SoftDeveloper"]/text()')
        self.add_xpath('sdk_support', '//label[@id="ctl00_AndroidMaster_Content_Apk_SoftSuitSdk"]/text()')
        self.add_xpath('category', '//label[@id="ctl00_AndroidMaster_Content_Apk_SoftCategory"]/text()')
        self.add_xpath('screen_support', '//label[@id="ctl00_AndroidMaster_Content_Apk_SupportScreen"]/text()')
        self.add_xpath('apk_size', '//label[@id="ctl00_AndroidMaster_Content_Apk_SoftSize"]/text()')
        self.add_xpath('language', '//label[@id="ctl00_AndroidMaster_Content_Apk_SoftLanguage"]/text()')
        self.add_xpath('publish_date', '//label[@id="ctl00_AndroidMaster_Content_Apk_SoftPublishTime"]/text()')
        self.add_xpath('downloads', '//label[@id="ctl00_AndroidMaster_Content_Apk_Download"]/text()')
        self.add_xpath('description', '//label[@id="ctl00_AndroidMaster_Content_Apk_Description"]')
        self.add_xpath('update_note', '//label[@id="ctl00_AndroidMaster_Content_Apk_SoftUpdateDescription"]')
        self.add_xpath('images', '//div[@class="screenimg"]//img/@src')  # '//label[@id="Apk_SoftImages"]//img/@src')
        #self.add_xpath('update_date', '//label[@id="Apk_SoftUpdateTime"]/text()')
        #self.add_xpath('update_description', '//label[@id="Apk_SoftUpdateDescription"]/text()')
        self.add_xpath('qr_link', '//input[@id="hiQRCode"]/@value')
        self.add_xpath('download_link', '//a[@class="linkbtn d1"]/@href')


class WandoujiaItemLoader(XPathItemLoader):

    def __init__(self, selector):
        self._selector = selector
        super(WandoujiaItemLoader, self).__init__(item=AppItem(), selector=self._selector)
        self._init_path()

    def _init_path(self):
        self.add_xpath('name', '//span[@itemprop="name"][@class="title"]/text()')
        self.add_xpath('icon_link', '//div[@class="app-icon"]/img[@itemprop="image"]/@src')
        #self.add_xpath('rating', '')
        self.add_xpath('sdk_support', '//dl[@class="infos-list"]/dd[5]/text()')
        self.add_xpath('version', '//dl[@class="infos-list"]/dd[4]/text()')
        self.add_xpath('developer', '//dl[@class="infos-list"]/dd[7]/text()')
        self.add_xpath('category', '//dd[@class="tag-box"]/a[1]/text()')
        self.add_xpath('apk_size', '//dl[@class="infos-list"]/dd[1]/text()')
        self.add_xpath('publish_date', '//dl[@class="infos-list"]/dd[3]/time/text()')
        self.add_xpath('downloads', '//i[@itemprop="interactionCount"]/text()')
        self.add_xpath('description', '//div[@itemprop="description"]/text()')
        self.add_xpath('images', '//div[@class="overview"]//img/@src')  # '//label[@id="Apk_SoftImages"]//img/@src')
        self.add_xpath('download_link', '//a[@class="install-btn"]/@href')
        self.add_xpath('update_note', '//div[@class="change-info"]/div[2]/text()')


class NoRedirectHandler(urllib2.HTTPRedirectHandler):

    def http_error_302(self, req, fp, code, msg, headers):
        result = urllib2.HTTPError(req.get_full_url(), code, msg, headers, fp)
        result.status = code
        return result
    http_error_301 = http_error_303 = http_error_307 = http_error_302


class AppChinaItemLoader(XPathItemLoader):

    opener = urllib2.build_opener(NoRedirectHandler())

    def get_real_url(self, url):
        oldurl = url
        if url.find('http://www.appchina.com') == 0:
            url = self.opener.open(url).headers.dict['location']
        if url.find('http://www.d.appchina.com') == 0:
            url = self.opener.open(url).headers.dict['location']
        log_info('get_real_url for url(%s) return url: %s' % (oldurl, url))
        return url

    def __init__(self, selector):
        self._selector = selector
        super(AppChinaItemLoader, self).__init__(item=AppItem(), selector=self._selector)
        self._init_path()

    def _init_path(self):
        self.add_xpath('name', '//h1[@class="ch-name cutoff fl"]/text()')
        self.add_xpath('icon_link', '//div[@class="app-name fl"]//img[@class="fl"]/@src')
        #self.add_xpath('rating', '//div[@class="result-mark"]/p/text()')
        self.add_xpath('version', '//div[@class="app-detailInfo"]/span[@class="version"]/text()')
        self.add_xpath('developer', '//span[@class="dl authon-name"]/text()')
        self.add_xpath('sdk_support', '//div[@class="app-detailInfo"]/span[@class="sys"]/text()')
        self.add_xpath('category', '//div[@class="search-title"]/a[3]/text()')
#        self.add_xpath('screen_support', '//label[@id="ctl00_AndroidMaster_Content_Apk_SupportScreen"]/text()')
        self.add_xpath('apk_size', '//div[@class="app-detailInfo"]/span[@class="size"]/text()')
#        self.add_xpath('language', '//label[@id="ctl00_AndroidMaster_Content_Apk_SoftLanguage"]/text()')
        self.add_xpath(
            'publish_date',
            '//div[@class="app-detailInfo-down cf"]/ul[@class="fl c-black info"]/li[4]/text()')
        self.add_xpath('downloads', '//div[@class="app-detailInfo"]/span[@class="down"]/em/text()')
        self.add_xpath('description', '//div[@class="scroll-content"]')
        self.add_xpath('images', '//div[@id="makeMeScrollable"]//img/@src')
        #self.add_xpath('update_date', '//label[@id="Apk_SoftUpdateTime"]/text()')
        #self.add_xpath('update_description', '//label[@id="Apk_SoftUpdateDescription"]/text()')
        self.add_xpath('qr_link', '//div[@class="qr-wrap cf"]/img/@src')
        log_info('load')
        try:
            url = self.get_xpath('//a[@class="zhushou-down fl"]/@meta-url')[0]
            self.add_value('download_link', self.get_real_url(url))
        except Exception as e:
            log_error('%s' % e)
            log_error(traceback.format_exc())
            self.add_xpath('download_link', '//a[@class="zhushou-down fl"]/@meta-url')


class MyAppItemLoader(XPathItemLoader):

    def __init__(self, selector):
        self._selector = selector
        super(MyAppItemLoader, self).__init__(item=AppItem(), selector=self._selector)
        self._init_path()

    def _init_path(self):
        self.add_xpath('name', '//header[@class="topsection"]/div[@class="app-msg"]/h1[@itemprop="name"]/text()')
        self.add_xpath('icon_link', '//header[@class="topsection"]/div[@class="app-img"]/img/@src')
        self.add_xpath('rating', '//header[@class="topsection"]/div[@class="app-msg"]//span[@itemprop="rating"]/text()')
        self.add_xpath('version', '//header[@class="topsection"]/div[@class="app-msg"]/dl/dd[6]/text()')
        self.add_xpath('developer', '//header[@class="topsection"]/div[@class="app-msg"]/dl/dd[9]/text()')
        self.add_xpath('sdk_support', '//header[@class="topsection"]/div[@class="app-msg"]/dl/dd[8]/text()')
        self.add_xpath('category', '//header[@class="topsection"]/div[@class="app-msg"]/dl/dd[4]/text()')
#        self.add_xpath('screen_support', '//label[@id="ctl00_AndroidMaster_Content_Apk_SupportScreen"]/text()')
        self.add_xpath('apk_size', '//header[@class="topsection"]/div[@class="app-msg"]/dl/dd[2]/text()')
        self.add_xpath('language', '//header[@class="topsection"]/div[@class="app-msg"]/dl/dd[5]/text()')
        self.add_xpath('publish_date', '//header[@class="topsection"]/div[@class="app-msg"]/dl/dd[7]/time/text()')
        self.add_xpath('downloads', '//header[@class="topsection"]/div[@class="app-msg"]/dl/dd[1]/text()')
        self.add_xpath('description', '//section/p[@itemprop="description"]')
        self.add_xpath('update_note', '//section/ul/li')
        self.add_xpath('images', '//section/div[@class="showpic"]//img/@data-url')
        #self.add_xpath('update_date', '//label[@id="Apk_SoftUpdateTime"]/text()')
        #self.add_xpath('update_description', '//label[@id="Apk_SoftUpdateDescription"]/text()')
        self.add_xpath('qr_link', '//div[@class="validate"]/img/@src')
        self.add_xpath('download_link', '//a[@class="downtopc"]/@href')


class YoutubeItemLoader(XPathItemLoader):

    def __init__(self, selector):
        self._selector = selector
        super(YoutubeItemLoader, self).__init__(item=YoutubeItem(), selector=self._selector)
        self.__init__path()

    def __init__path(self):
        self.add_xpath('name', '//span[@id="eow-title"]/text()')
        self.add_xpath('likes', '//span[@class="likes"]/text()')
        self.add_xpath('dislikes', '//span[@class="dislikes"]/text()')
        self.add_xpath('duration', '//meta[@itemprop="duration"]/@content')
        self.add_xpath('view_count', '//span[@class="watch-view-count"]/strong/text()')
        self.add_xpath('author', '//a[@rel="author"]/text()')
        self.add_xpath('category', '//p[@id="eow-category"]/a/text()')
        self.add_xpath('publish_date', '//span[@id="eow-date"]/text()')
        self.add_xpath('comments', '//span[@class="comments-section-stat"]/text()')
        self.add_xpath('description', '//p[@id="eow-description"]/text()')


class YelpItemLoader(XPathItemLoader):

    def __init__(self, selector):
        self._selector = selector
        super(YelpItemLoader, self).__init__(item=YelpItem(), selector=self._selector)
        self.__init__path()

    def __init__path(self):
        self.add_xpath('name', '//h1[@itemprop="name"]/text()')
        self.add_xpath('rating', '//div[@itemprop="aggregateRating"]/div/i/@title')
        self.add_xpath('reviews', '//span[@itemprop="reviewCount"]/text()')
        self.add_xpath('category', '//span[@id="cat_display"]/a/text()')
        self.add_xpath('price', '//span[@id="price_tip"]/text()')
        self.add_xpath('city', '//address[@itemprop="address"]/text()')
        self.add_xpath('address', '//span[@itemprop="streetAddress"]/text()')
        self.add_xpath('phone', '//span[@id="bizPhone"]/text()')
#        self.add_xpath('longitude_latitude', '//meata[@id="STATIC_MAP"]/span/img/@src')
        self.add_xpath('owner_website', '//div[@id="bizUrl"]/a/text()')
        longitude_latitude = self.get_xpath('//meta[@property="og:longitude"]/@content') + \
            self.get_xpath('//meta[@property="og:latitude"]/@content')
        longitude_latitude = ','.join(longitude_latitude)
        self.add_value('longitude_latitude', longitude_latitude)


class TripAdvisorItemLoader(XPathItemLoader):

    def __init__(self, selector):
        self._selector = selector
        super(TripAdvisorItemLoader, self).__init__(item=TripAdvisorItem(), selector=self._selector)
        self.__init__path()

    def __init__path(self):
        self.add_xpath('name', '//h1[@id="HEADING"]/text()')
        self.add_xpath(
            'rating',
            '//div[@id="ICR2"]/div/div/div[@class="rs rating"]/span/img[@class="sprite-ratings"]/@alt')
        self.add_xpath(
            'reviews',
            '//div[@id="ICR2"]/div/div/div[@class="rs rating"]/span/span[@property="v:count"]/text()')
        self.add_xpath('price', '//span[@property="v:pricerange"]/text()')
        self.add_xpath('city', '//span[@property="v:locality"]/text()')
        self.add_xpath('address', '//span[@class="street-address"]/text()')
#        self.add_xpath('phone', '//div[@class="odcHotel blDetails detailAdjust "]/div/div/text()')
        self.add_xpath('hotel_class', '//img[@title="Hotel class"]/@alt')
        self.add_xpath('rank_of_city', '//div[@class="slim_ranking"]/node()')
        self.add_xpath('longitude_latitude', '//div[@id="STATIC_MAP"]/span/img/@src')
        self.add_xpath('owner_website', '//div[@class="odcHotel blDetails detailAdjust "]/div/div/a/@href')
        scripts = self.get_xpath('//script[@type="text/javascript"]/text()')
        res = ''
        for script in scripts:
            if '"priority":500' in script:
                for line in script.split('id'):
                    if '"priority":500' in line:
                        if 'google' in line:
                            res = line.split('center=')[1].split('&')[0]
                        elif 'virtualearth' in line:
                            res = line.split('Road/')[1].split('/')[0]
        self.add_value('longitude_latitude', res)


class AppleItemLoader(XPathItemLoader):

    def __init__(self, selector):
        self._selector = selector
        super(AppleItemLoader, self).__init__(item=AppleItem(), selector=self._selector)
        self._init_path()

    def _init_path(self):
        self.add_xpath('name', '//div[@id="title"]//h1/text()')
        self.add_xpath('icon_link', '//div[@id="left-stack"]/div[1]//img/@src')
#        self.add_xpath('current_rating', '//div[@class="extra-list customer-ratings"]/div[2]/@aria-label')
        self.add_xpath('rating', '//div[@class="extra-list customer-ratings"]/div[4]/@aria-label')
        self.add_xpath('version', '//div[@id="left-stack"]/div[1]/ul/li[4]/text()')
        self.add_xpath('developer', '//div[@id="title"]//h2/text()')
        self.add_xpath('sdk_support', '//div[@id="left-stack"]/div[1]/p/text()')
        self.add_xpath('category', '//div[@id="left-stack"]/div[1]/ul/li[@class="genre"]/a/text()')
        self.add_xpath('screen_support', '//div[@class="mainsoft_center"]/ul/li[4]/p/text()')
        self.add_xpath('apk_size', '//div[@id="left-stack"]/div[1]/ul/li[5]/text()')
        self.add_xpath('language', '//div[@id="left-stack"]/div[1]/ul/li[@class="language"]/text()')
#        self.add_xpath('association', '//div[@class="app-rating"]/a/text()')
        self.add_xpath('publish_date', '//div[@id="left-stack"]/div[1]/ul/li[@class="release-date"]/text()')
#        self.add_xpath('downloads', '//div[@class="doc-metadata"]//dd[@itemprop="numDownloads"]/text()')
        self.add_xpath('description', '//div[@class="product-review"]/p')
        self.add_xpath('images', '//div[@class="swoosh lockup-container application large screenshots"]//img/@src')
        self.add_xpath('price', '//div[@id="left-stack"]/div[1]//div[@class="price"]/text()')
        #self.add_xpath('download_link', '//div[@class="tocomp"]/h3[@class="down_1"]/a/@href')


class GoApkItemLoader(XPathItemLoader):

    def __init__(self, selector):
        self._selector = selector
        super(GoApkItemLoader, self).__init__(item=AppItem(), selector=self._selector)
        self._init_path()

    def _init_path(self):
        self.add_xpath('name', '//div[@class="detail_description"]/div[1]/h3/text()')
        self.add_xpath('icon_link', '//div[@class="detail_icon"]/img/@src')
        self.add_xpath('rating', '//div[@class="detail_description"]/div[2]/div/@style')
        self.add_xpath('version', '//div[@class="detail_description"]/div[1]/span[1]/text()')
        self.add_xpath('developer', '//div[@class="detail_description"]/div[4]/span[1]/text()')
        self.add_xpath('category', '//ul[@id="detail_line_ul"]/li[1]/text()')
        self.add_xpath('apk_size', '//ul[@id="detail_line_ul"]/li[4]/span[1]/text()')
        self.add_xpath('publish_date', '//ul[@id="detail_line_ul"]/li[3]/text()')
        self.add_xpath('downloads', '//ul[@id="detail_line_ul"]/li[2]/span[1]/text()')
        self.add_xpath('description', '//div[@class="app_detail_infor"]/p')
        self.add_xpath('images', '//ul[@id="detail_slider_ul"]//img/@src')
        #self.add_xpath('update_date', '//label[@id="Apk_SoftUpdateTime"]/text()')
        self.add_xpath('qr_link', '//div[@id="i_code"]/img/@src')
        self.add_xpath('download_link', '//div[@class="detail_down"]/a/@onclick')


class NDuoAItemLoader(XPathItemLoader):

    def __init__(self, selector):
        self._selector = selector
        super(NDuoAItemLoader, self).__init__(item=AppItem(), selector=self._selector)
        self._init_path()

    def _init_path(self):
        self.add_xpath('name', '//div[@class="apkinfo"]//div[@class="name"]/span[@class="title"]/text()')
        self.add_xpath('icon_link', '//div[@class="apkinfo"]//div[@class="icon"]/img/@src')
        self.add_xpath('rating', '//div[@class="apkinfo"]//div[@class="starWrap"]/span[@class="star"]/s/@class')
        self.add_xpath('version', '//div[@class="apkinfo"]//div[@class="name"]/span[@class="version"]/text()')
        self.add_xpath('developer', '//div[@class="apkinfo"]/div[@class="author row"]/span/a/text()')
        self.add_xpath('sdk_support', '//div[@class="apkinfo"]/div[@class="adapt row popup"]/h4/text()')
        self.add_xpath('category', '//div[@id="breadcrumbs"]/span[3]/a/text()')
        self.add_xpath(
            'screen_support',
            '//div[@class="apkinfo"]/div[@class="resolution row popup"]/div[@class="hide_p"]/p/text()')
        self.add_xpath('apk_size', '//div[@class="apkinfo"]//div[@class="size row"]/text()')
        #self.add_xpath('language', '')
        # use update_date as publish_date
        self.add_xpath('publish_date', '//div[@class="apkinfo"]/div[@class="updateTime row"]/em/text()')
        self.add_xpath('downloads', '//div[@class="apkinfo"]//div[@class="levelCount"]/span[@class="count"]/text()')
        self.add_xpath('description', '//div[@id="detailInfo"]//div[@class="inner"]/node()')  # a piece html fragment
        self.add_xpath('images', '//ul[@class="shotbox"]//img/@src')
        #self.add_xpath('update_date', '//div[@class="time"]/text()')
        #self.add_xpath('update_description', '')
        self.add_xpath('qr_link', '//div[@class="barcode"]/img/@src')
        self.add_xpath('download_link', '//a[@class="d_pc_normal"]/@href')


class MumayiItemLoader(XPathItemLoader):

    def __init__(self, selector):
        self._selector = selector
        super(MumayiItemLoader, self).__init__(item=AppItem(), selector=self._selector)
        self._init_path()

    def _init_path(self):
        self.add_xpath('name', '//div[@class="mainsoft_header"]/h1[@id="titleInner"]/text()')
        self.add_xpath('icon_link', '//a[@class="img3"]/img/@src')
        self.add_xpath('rating', '//div[@class="titr stars"]/a/@class')
        # self.add_xpath('version', '//a[@id="titleInner"]/text()') #compose with name
#        self.add_xpath('developer', '//div[@class="left"]/div[4]/text()')
        self.add_xpath('sdk_support', '//div[@id="layer92"]/text()')
        self.add_xpath('category', '//div[@class="topbar"]/div/a[3]/text()')
        self.add_xpath('screen_support', '//em[@class="titr breakword lh24"]/text()')
        self.add_xpath('apk_size', '//ul[@class="info202 lh32"]/li[6]/em[2]/text()')
        #self.add_xpath('language', '')
        # use update_date as publish_date
        self.add_xpath('publish_date', '//ul[@class="info202 lh32"]/li[5]/em[2]/text()')
        self.add_xpath('downloads', '//span[@class="downscrollLoading"]/text()')
        # a piece html fragment
        self.add_xpath('description', '//div[@class="pinglun_center"]/div[@class="appinfo_box"]/p/node()')
        self.add_xpath('images', '//div[@class="pinglun_center"]/div[@class="appinfo_box"]//center/img/@src2')
        #self.add_xpath('update_date', '//div[@class="time"]/text()')
        #self.add_xpath('update_description', '')
        self.add_xpath('qr_link', '//div[@class="img148"]/img/@src')
        self.add_xpath('download_link', '//a[@class="download fl"]/@href')


class Aimi8ItemLoader(XPathItemLoader):

    def __init__(self, selector):
        self._selector = selector
        super(Aimi8ItemLoader, self).__init__(item=AppItem(), selector=self._selector)
        self._init_path()

    def _init_path(self):
        self.add_xpath('name', '//div[@class="basic_info"]/table//tr[1]/td/label/text()')
        self.add_xpath('icon_link', '//div[@class="basic_info"]/div[@class="icon"]/img/@src')
        self.add_xpath('rating', '//div[@class="basic_info"]/table//tr[2]/td/span/text()')
        self.add_xpath('version', '//div[@class="basic_info"]/table//tr[3]/td[1]/text()')
        self.add_xpath('developer', '//div[@class="basic_info"]/table//tr[3]/td[2]/text()')
        #self.add_xpath('sdk_support', '//div[@class="mainsoft_center"]//ul/li[3]/text()')
        self.add_xpath('category', '//div[@class="sitemap"]/a[3]/text()')
        #self.add_xpath('screen_support', '//div[@class="mainsoft_center"]//ul/li[4]/p/text()')
        self.add_xpath('apk_size', '//div[@class="basic_info"]/table//tr[5]/td[1]/text()')
        self.add_xpath('language', '//div[@class="basic_info"]/table//tr[4]/td[1]/text()')
        # use update_date as publish_date
        self.add_xpath('publish_date', '//div[@class="basic_info"]/table//tr[4]/td[2]/text()')
        self.add_xpath('downloads', '//div[@class="basic_info"]/table//tr[5]/td[2]/text()')
        self.add_xpath('description', '//div[@class="dsp"]/node()')  # a piece html fragment
        self.add_xpath('images', '//div[@id="container"]/script[contains(text(),"rotator_content")]')
        #self.add_xpath('update_date', '//div[@class="time"]/text()')
        #self.add_xpath('update_description', '')
        self.add_xpath('qr_link', '//div[@class="download_way"]//img[@class="qr"]/@src')
        self.add_xpath('download_link', '//div[@class="download_way"]//a[@onclick="to_download()"]/@href')


class EoeItemLoader(XPathItemLoader):

    def __init__(self, selector):
        self._selector = selector
        super(EoeItemLoader, self).__init__(item=AppItem(), selector=self._selector)
        self._init_path()

    def _init_path(self):
        self.add_xpath('name', '//div[@class="md_top"]/dl/dt/h1/text()')
        self.add_xpath('icon_link', '//div[@class="md_top"]/a/img/@src')
        self.add_xpath('rating', '//div[@class="md_top"]/dl/dd[1]/i/@title')
        self.add_xpath('version', '//div[@class="md_top"]/dl/dt/span/text()')
        #self.add_xpath('developer', '//div[@class="basic_info"]/table//tr[3]/td[2]/text()')
        self.add_xpath('sdk_support', '//div[@class="md_top"]/dl/dd[3]/text()')
        self.add_xpath('category', '//div[@class="hot_r "]/span/a/text()')
        #self.add_xpath('screen_support', '//div[@class="mainsoft_center"]//ul/li[4]/p/text()')
        self.add_xpath('apk_size', '//div[@class="md_top"]/dl/dd[2]/text()')
        #self.add_xpath('language', '//div[@class="basic_info"]/table//tr[4]/td[1]/text()')
        # self.add_xpath('publish_date', '//div[@class="basic_info"]/table//tr[4]/td[2]/text()') #use update_date as publish_date
        #self.add_xpath('downloads', '//div[@class="basic_info"]/table//tr[5]/td[2]/text()')
        self.add_xpath('description', '//div[@class="d_details"]/node()')  # a piece html fragment
        self.add_xpath('images', '//div[@class="screenshot-out"]/table//td/img/@src')
        #self.add_xpath('update_date', '//div[@class="time"]/text()')
        #self.add_xpath('update_description', '')
        #self.add_xpath('qr_link', '//div[@class="download_way"]//img[@class="qr"]/@src')
        self.add_xpath('download_link', '//div[@class="tocomp"]/h3[@class="down_1"]/a/@href')


class GoogleItemLoader(XPathItemLoader):

    def __init__(self, selector):
        self._selector = selector
        super(GoogleItemLoader, self).__init__(item=AppItem(), selector=self._selector)
        self._init_path()

    def _init_path(self):
        self.add_xpath('name', '//div[@class="doc-banner-container"]//h1[@class="doc-banner-title"]/text()')
        self.add_xpath('icon_link', '//div[@class="doc-banner-icon"]/img/@src')
        self.add_xpath('rating', '//div[@class="doc-overview-reviews"]//div[@class="average-rating-value"]/text()')
        self.add_xpath('version', '//div[@class="doc-metadata"]/dl/dd[@itemprop="softwareVersion"]/text()')
        self.add_xpath('developer', '//a[@class="doc-header-link"]/text()')
        self.add_xpath('sdk_support', '//div[@class="doc-metadata"]//dd[4]/text()')
        self.add_xpath('category', '//div[@class="doc-metadata"]//dd[5]/a/text()')
        self.add_xpath('screen_support', '//div[@class="mainsoft_center"]//ul/li[4]/p/text()')
        self.add_xpath('apk_size', '//div[@class="doc-metadata"]//dd[@itemprop="fileSize"]/text()')
#        self.add_xpath('language', '//div[@class="basic_info"]/table//tr[4]/td[1]/text()')
        # use update_date as publish_date
        self.add_xpath('publish_date', '//div[@class="doc-metadata"]//dd[2]/time/text()')
        self.add_xpath('downloads', '//div[@class="doc-metadata"]//dd[@itemprop="numDownloads"]/text()')

        description = self.get_xpath('//div[@class="doc-whatsnew-container"]//*//text()')
        if description == [u'\u6700\u8fd1\u6ca1\u6709\u66f4\u6539\u3002'] or \
           description == [u'\u6700\u8fd1\u6c92\u6709\u8b8a\u66f4\u3002']:
            description = self.get_xpath('//div[@id="doc-original-text"]/node()')
        else:
            description = self.get_xpath('//div[@id="doc-original-text"]/node()') + \
                self.get_xpath('//div[@class="doc-whatsnew-container"]/node()')
            description = string.join(description)

        self.add_value('description', description)  # a piece html fragment
        self.add_xpath('images', '//div[@class="screenshot-carousel-content-container"]/img/@src')
        #self.add_xpath('update_date', '//div[@class="time"]/text()')
        #self.add_xpath('update_description', '')
        #self.add_xpath('qr_link', '//div[@class="download_way"]//img[@class="qr"]/@src')
        #self.add_xpath('download_link', '//div[@class="tocomp"]/h3[@class="down_1"]/a/@href')


class ThreeGSoftItemAdapter(XPathItemLoader):

    def __init__(self, selector):
        self._selector = selector
        super(ThreeGSoftItemAdapter, self).__init__(item=AppItem(), selector=self._selector)
        self._init_path()

    def _init_path(self):
        name = self.get_xpath('//div[@class="soft-detail"]/span[1]/text()')
        update_date = self.get_xpath('//div[@class="soft-detail"]/span[1]/em/text()')
        self.add_value('name', name)
        self.add_value('publish_date', update_date)  # use update_date as publish_date

        self.add_xpath('icon_link', '//div[@class="soft-detail"]/strong/img/@src')
        self.add_xpath('rating', '//div[@class="soft-detail"]/span[2]/em/img/@src')
        self.add_xpath('version', '//div[@class="info"]/ul/li[2]/text()')
        #self.add_xpath('developer', '//div[@class="basic_info"]/table//tr[3]/td[2]/text()')
        self.add_xpath('sdk_support', '//div[@class="info"]/ul/li[1]/text()')
        self.add_xpath('category', '//header/nav/a[5]/text()')
        #self.add_xpath('screen_support', '//div[@class="mainsoft_center"]//ul/li[4]/p/text()')
        self.add_xpath('apk_size', '//div[@class="info"]/ul/li[5]/text()')
        self.add_xpath('language', '//div[@class="info"]/ul/li[4]/text()')
        #self.add_xpath('update_date', '//div[@class="basic_info"]/table//tr[4]/td[2]/text()')
        self.add_xpath('downloads', '//div[@class="info"]/ul/li[3]/text()')
        self.add_xpath('description', '//div[@class="info"]/ul/li[6]/node()')  # a piece html fragment
        self.add_xpath('images', '//div[@class="rail-content"]//img/@src')
        #self.add_xpath('update_description', '')
        #self.add_xpath('qr_link', '//div[@class="download_way"]//img[@class="qr"]/@src')
        self.add_xpath('download_link', '//div[@class="soft-detail"]/span[2]/a[@class="download"]/@href')


class ThreeGGameItemAdapter(XPathItemLoader):

    def __init__(self, selector):
        self._selector = selector
        super(ThreeGGameItemAdapter, self).__init__(item=AppItem(), selector=self._selector)
        self._init_path()

    def _init_path(self):
        self.add_xpath('name', '//div[@class="soft"]/div[@class="soft_info"]/div[@class="soft_name"]/text()')
        self.add_xpath('icon_link', '//div[@class="soft"]/div[@class="map"]/img/@src')
        self.add_xpath('rating', '//div[@class="soft"]/div[@class="soft_dl"]/div[2]/img/@src')
        # name contain version
        self.add_xpath('version', '//div[@class="soft"]/div[@class="soft_info"]/div[@class="soft_name"]/text()')
        #self.add_xpath('developer', '//div[@class="basic_info"]/table//tr[3]/td[2]/text()')
        self.add_xpath('sdk_support', '//div[@class="intro"]/div[4]/text()')
        self.add_xpath('category', '//div[@class="soft"]/div[@class="soft_info"]/div[3]/a/span/text()')
        self.add_xpath('screen_support', '//div[@class="intro"]/div[5]/text()')
        self.add_xpath('apk_size', '//div[@class="intro"]/div[1]/text()')
        self.add_xpath('language', '//div[@class="intro"]/div[3]/text()')
        # use update_date as publish_date
        self.add_xpath('publish_date', '//div[@class="soft"]/div[@class="soft_info"]/div[2]/text()')
        self.add_xpath('downloads', '//div[@class="intro"]/div[2]/text()')
        self.add_xpath('description', '//div[@class="intro"]/div[6]/node()')  # a piece html fragment
        self.add_xpath('images', '//div[@class="soft_img"]/img/@src')
        #self.add_xpath('update_date', '//div[@class="time"]/text()')
        #self.add_xpath('update_description', '')
        #self.add_xpath('qr_link', '//div[@class="download_way"]//img[@class="qr"]/@src')
        self.add_xpath('download_link', '//div[@class="soft"]/div[@class="soft_dl"]/div[1]/a/@href')

