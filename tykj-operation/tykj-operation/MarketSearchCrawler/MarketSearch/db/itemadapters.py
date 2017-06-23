# coding=utf-8
'''
Created on Jun 2, 2011

@author: yan
'''
from BeautifulSoup import BeautifulSoup
from MarketSearch.utils import get_epoch_datetime, log_error
from datetime import datetime, timedelta
import hashlib
import httplib
import market
import re
import sys
import urllib
import urllib2

reload(sys)
getattr(sys, 'setdefaultencoding')("utf-8")


class ItemAdapterFactory(object):

    @staticmethod
    def get_itemadapter(source=None):
        if not source:
            return None

        if source == HiApkItemAdapter.source:
            return HiApkItemAdapter()
        elif source == WandoujiaItemAdapter.source:
            return WandoujiaItemAdapter()
        elif source == BaiduItemAdapter.source:
            return BaiduItemAdapter()
        elif source == QihuItemAdapter.source:
            return QihuItemAdapter()
        elif source == OneMobileItemAdapter.source:
            return OneMobileItemAdapter()
        elif source == OneMobileAPIItemAdapter.source:
            return OneMobileAPIItemAdapter()
        elif source == GooglePlayItemAdapter.source:
            return GooglePlayItemAdapter()
        elif source == XiaomiThemeItemAdapter.source:
            return XiaomiThemeItemAdapter()
        elif source == NineOneIphoneItemAdapter.source:
            return NineOneIphoneItemAdapter()
        elif source == NineOneItemAdapter.source:
            return NineOneItemAdapter()
        elif source == NineOneImageItemAdapter.source:
            return NineOneImageItemAdapter()
        elif source == AppChinaItemAdapter.source:
            return AppChinaItemAdapter()
        elif source == MyAppItemAdapter.source:
            return MyAppItemAdapter()
        elif source == NDuoAItemAdapter.source:
            return NDuoAItemAdapter()
        elif source == GoApkItemAdapter.source:
            return GoApkItemAdapter()
        elif source == MumayiItemAdapter.source:
            return MumayiItemAdapter()
        elif source == GoogleItemAdapter.source:
            return GoogleItemAdapter()
        elif source == TripAdvisorItemAdapter.source:
            return TripAdvisorItemAdapter()
        elif source == AppleItemAdapter.source:
            return AppleItemAdapter()
        elif source == YelpItemAdapter.source:
            return YelpItemAdapter()
        elif source == YoutubeItemAdapter.source:
            return YoutubeItemAdapter()

        return None


class YelpItemAdapter(object):

    source = 'yelp.com'

    def adapt(self, item):
        if 'rating' in item and item['rating'] != '':
            item['rating'] = self.get_rating(item['rating'])
        return item

    def get_rating(self, rating):
        rating = rating.split()[0].strip()
        return rating


class YoutubeItemAdapter(object):

    source = 'youtube.com'
    _month_map_dict = {u'Jan': '01', u'Feb': '02', u'Mar': '03', u'Apr': '04', u'May': '05', u'Jun': '06',
                       u'Jul': '07', u'Aug': '08', u'Sep': '09', u'Oct': '10', u'Nov': '11', u'Dec': '12'}

    def adapt(self, item):
        if 'comments' in item and item['comments'] != '':
            item['comments'] = item['comments'][1:-1]
        if 'duration' in item and item['duration'] != '':
            item['duration'] = self._get_duration(item['duration'])
        if 'likes' in item and item['likes'] != '':
            item['likes'] = item['likes'].replace(',', '')
        if 'dislikes' in item and item['dislikes'] != '':
            item['dislikes'] = item['dislikes'].replace(',', '')
        if 'view_count' in item and item['view_count'] != '':
            item['view_count'] = item['view_count'].replace(',', '')
        if 'publish_date' in item and item['publish_date'] != '':
            item['publish_date'] = self._get_publish_date(item['publish_date'])

        return item

    def _get_duration(self, duration):
        min = duration.split('M')[0].split('PT')[1]
        sec = duration.split('M')[1].split('S')[0]
        duration = "%s:%s" % (min, sec)
        return duration

    def _get_publish_date(self, datetime_str):
        if not datetime_str:
            return None
        month = self._month_map_dict.get(datetime_str.split()[0].strip())
        day = datetime_str.split()[1].split(',')[0].strip()
        year = datetime_str.split(',')[1].strip()
        date = datetime.strptime(year + month + day, "%Y%m%d")
        return get_epoch_datetime(date)


class TripAdvisorItemAdapter(object):

    source = 'tripadvisor.com'

    def adapt(self, item):
#        if 'phone' in item and item['phone'] != '':
#            item['phone'], item['owner_website'] = self.get_detail(item['phone'])

        if 'owner_website' in item and item['owner_website'] != '':
            item['owner_website'] = "http://www.tripadvisor.com%s" % item['owner_website']

        if 'rank_of_city' in item and item['rank_of_city'] != '':
            item['rank_of_city'] = self.get_rank(item['rank_of_city'])

        if 'hotel_class' in item and item['hotel_class'] != '':
            item['hotel_class'] = self.get_rating(item['hotel_class'])

        if 'rating' in item and item['rating'] != '':
            item['rating'] = self.get_rating(item['rating'])

        item['category'] = "hotel"

        return item

    def get_rank(self, rank):
        rank = rank[0].split('#')[1].split('<')[0] + rank[1]
        return rank

    def get_rating(self, rating):
        rating = rating.split('of')[0].strip()
        return rating


class ItemAdapter(object):

    def adapt(self, item):
        if 'icon_link' in item and item['icon_link'] != '':
            item['icon_path'] = self._get_icon_path(item['icon_link'])
        if 'images' in item and item['images'] != '':
            item['images_path'] = self._get_images_path(item['images'])

    def _get_icon_path(self, icon_link):
        image_guid = hashlib.sha1(icon_link).hexdigest()
        return 'full/%s/%s/%s.%s' % (image_guid[:1], image_guid[1:3], image_guid, icon_link.split('.')[-1])

    def _get_images_path(self, images):
        images_path = []
        for image in images.split():
            image_guid = hashlib.sha1(image).hexdigest()
            image_path = 'full2/%s/%s/%s.jpg' % (image_guid[:1], image_guid[1:3], image_guid)
            images_path.append(image_path)
        return ' '.join(images_path)


class AppleItemAdapter(ItemAdapter):

    source = 'itunes.apple.com'

    def adapt(self, item):
        super(self.__class__, self).adapt(item)
        if 'rating' in item:
            item['rating'], item['downloads'] = self._get_rating(item['rating'])
        if 'apk_size' in item:
            item['apk_size'] = _adapt_apk_size(item['apk_size'])
        if 'developer' in item:
            item['developer'] = _adapt_colon_str(item['developer'], 1)
        if 'current_rating' in item:
            item['current_rating'], item['current_rating_num'] = self._get_rating(item['current_rating'])
        if 'publish_date' in item:
            item['publish_date'] = self._get_publish_date(item['publish_date'])
        if 'price' in item:
            item['price'] = self._get_price(item['price'])
        item['download_link'] = '_'.join([item['source_link'], item['version']])
        item['source_link'] = item['download_link']
        item['app_id'] = item['source_link'].split('?mt')[0].split('/id')[-1]
        if item.get('app_id') and item.get('category') == u'\u6e38\u620f':
            item['category'] = market.get_category(item['app_id'])
        item['apple_id'] = market.get_apple_id(item['app_id'])
        item['description'] = _adapt_desc_str(item.get('description', ''))
        return item

    def _get_price(self, price):
        if u'\u514d\u8d39' in price:
            price = 0
        else:
            price = price[1:]
        return price

    def _get_rating(self, rating):
        self.rating = rating.split(u'\u661f')[0]
        self.rating_num = rating.split(',')[1].split()[0].strip()
        return self.rating, self.rating_num

    def _get_publish_date(self, datetime_str):
        if not datetime_str:
            return None
        year = datetime_str.split(u'\u5e74')[0]
        month = datetime_str.split(u'\u5e74')[1].split(u'\u6708')[0]
        day = datetime_str.split(u'\u6708')[1].split(u'\u65e5')[0]
        date = datetime.strptime(year + month + day, "%Y%m%d")
        return get_epoch_datetime(date)


class XiaomiThemeItemAdapter(ItemAdapter):

    source = 'zhuti.xiaomi.com'
    _base_url = 'http://zhuti.xiaomi.com'

    def adapt(self, item):
        super(self.__class__, self).adapt(item)
        if 'category' in item:
            if item['category'] == u'\u767e\u53d8\u9501\u5c4f':
                item['source'] = 'lock.xiaomi.com'
            elif item['category'] == u'\u56fe\u6807':
                item['source'] = 'icon.xiaomi.com'
            elif item['category'] == u'\u5b57\u4f53':
                item['source'] = 'font.xiaomi.com'
#        if 'rating' in item:
#            item['rating'] = self._get_rating(item['rating'])
        if 'description' in item:
            self._get_detail_info(item)
        if 'download_link' in item:
            item['download_link'] = self._base_url + item['download_link']
        if 'images' in item and len(item['images'].split()) > 4:
            item['images'] = ' '.join(item['images'].split()[:5])
            item['images_path'] = ' '.join(item['images_path'].split()[:5])
        item['rating'] = self._get_rating(item['source_link'])
        return item

    def _get_detail_info(self, item):
        info_list = item['description'].split('<br>')
        item['description'] = item.get('version').strip()
        for info in info_list:
            if u'\u4f5c\u8005\uff1a' in info:
                item['developer'] = info.split(u'</span>')[1].strip()
                if item['developer']:
                    item['developer'] = item['developer'].split()[0]
            if u'\u8bbe\u8ba1\u5e08\uff1a' in info:
                item['sdk_support'] = info.split(u'</span>')[1].strip()
                if item['sdk_support']:
                    item['sdk_support'] = item['sdk_support'].split()[0]
            if u'\u7248\u672c\uff1a' in info:
                item['version'] = info.split(u'</span>')[1].strip()
                if item['version']:
                    item['version'] = item['version'].split()[0]
            if u'\u5927\u5c0f\uff1a' in info:
                item['apk_size'] = info.split(u'</span>')[1].strip()
                if item['apk_size']:
                    item['apk_size'] = _adapt_apk_size(item['apk_size'].split()[0])
            if u'\u4e0b\u8f7d\uff1a' in info:
                item['downloads'] = info.split(u'</span>')[1].strip()
                if item['downloads']:
                    item['downloads'] = item['downloads'].split()[0].split('+')[0]
            if u'\u66f4\u65b0\u65f6\u95f4\uff1a' in info:
                item['publish_date'] = info.split(u'</span>')[1].strip()
                if item['publish_date']:
                    item['publish_date'] = _adapt_date_str(item['publish_date'].split()[0])
            if u'\u5305\u542b\u6a21\u5757\uff1a' in info:
                item['screen_support'] = info.split(u'</span>')[1].strip()
                if item['screen_support']:
                    item['screen_support'] = item['screen_support'].split()[0]

    def _get_rating(self, url):
        request_url = "/comment/listall/%s" % url.split('/')[-1]
        conn = httplib.HTTPConnection('zhuti.xiaomi.com')
        conn.request("GET", request_url, headers={"Host": "zhuti.xiaomi.com",
                                                  "Referer": url,
                                                  "User-Agent":
                                                  "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.95 Safari/537.11",
                                                  "X-Requested-With": "XMLHttpRequest"})
        response = conn.getresponse()
        data = response.read()
        rating = float(data.split('score":')[1].split(",")[0]) / 2
        return rating


class QihuItemAdapter(ItemAdapter):

    source = 'zhushou.360.cn'

    def adapt(self, item):
        super(self.__class__, self).adapt(item)
        if 'rating' in item:
            item['rating'] = self._get_rating(item['rating'])
        if 'downloads' in item:
            item['downloads'] = self._get_downloads(item['downloads'])
        if 'publish_date' in item:
            item['publish_date'] = _adapt_date_str(_adapt_colon_str(item['publish_date'], 1))
        if 'screen_support' in item:
            self._get_detail_info(item)
        if 'download_link' in item:
            self._get_download_link(item)
        item['description'] = _adapt_desc_str(item.get('description', ''))
        item['source_link'] = item.get('source_link') + '?' + str(item.get('publish_date', 1))
        return item

    def _get_detail_info(self, item):
        info_list = item['screen_support'].split('<td>')
        item['screen_support'] = None
        for info in info_list:
            if u'\u5206\u7c7b\uff1a' in info:
                item['category'] = info.split(u'\u5206\u7c7b\uff1a')[1].split('<')[0].strip()
            if u'\u4f5c\u8005\uff1a' in info:
                item['developer'] = info.split(u'\u4f5c\u8005\uff1a')[1].split('<')[0].strip()
            if u'\u7248\u672c\uff1a' in info:
                item['version'] = info.split(u'\u7248\u672c\uff1a')[1].split('<')[0].strip()
            if u'\u7cfb\u7edf\uff1a' in info:
                item['sdk_support'] = info.split(u'\u7cfb\u7edf\uff1a')[1].split('<')[0].strip()
            if u'\u8bed\u8a00\uff1a' in info:
                item['language'] = info.split(u'\u8bed\u8a00\uff1a')[1].split('<')[0].strip()

    def _get_download_link(self, item):
        item['apk_size'] = _adapt_apk_size(item['download_link'].split("size':'")[1].split("'")[0])
        item['download_link'] = item['download_link'].split("'downurl':'")[1].split("'")[0]

    def _get_rating(self, rating):
        rating = float(rating[:-1].strip()) / 2
        return rating

    def _get_downloads(self, downloads):
        downloads = _adapt_colon_str(downloads, 1)[:-1]
        return downloads


class WandoujiaItemAdapter(ItemAdapter):

    source = 'wandoujia.com'

    def adapt(self, item):
        super(self.__class__, self).adapt(item)
        if 'downloads' in item:
            item['downloads'] = self._get_downloads(item['downloads'])
        if 'publish_date' in item:
            item['publish_date'] = self._get_date(item['publish_date'])
        if 'apk_size' in item:
            item['apk_size'] = _adapt_apk_size(item['apk_size'])
        item['description'] = _adapt_desc_str(item.get('description', ''))
        item['download_link'] = item.get('source_link').replace('http://www', 'http://apps') \
            + '/download?' + str(item.get('publish_date', 1))
        unique_source_link(item)

        return item

    def _get_date(self, date):
        if date.find(u'昨天') > -1:
            return self._date_begin(datetime.now() - timedelta(days=1))
        elif date.find(u'今天') > -1:
            return self._date_begin(datetime.now())
        date = date.replace(u'月', '-')
        date = date.replace(u'日', '')
        if date.find(u'年') > -1:
            date = date.replace(u'年', '-')
        else:
            date = '2013-%s' % date
        return _adapt_date_str(date)

    def _date_begin(self, date):
        return get_epoch_datetime(datetime.strptime(date.strftime('%Y%m%d'), '%Y%m%d'))

    def _get_downloads(self, downloads):
        if u'\u5343' in downloads:
            downloads = float(downloads.split(u'\u5343')[0]) * 1000
        elif u'\u4e07' in downloads:
            downloads = float(downloads.split(u'\u4e07')[0]) * 10000
        elif u'\u4ebf' in downloads:
            downloads = float(downloads.split(u'\u4ebf')[0]) * 1000000000
        else:
            downloads = float(downloads)
        return downloads


class BaiduItemAdapter(ItemAdapter):

    source = 'as.baidu.com'
    _base_url = 'http://m.baidu.com/app?ext=appmobile&action=content&docid='

    def adapt(self, item):
        super(self.__class__, self).adapt(item)
        if 'icon_link' in item:
            item['icon_link'] = item['icon_link'].replace('.jpg', '.png')
            item['icon_path'] = self._get_icon_path(item['icon_link'])
        if 'rating' in item:
            item['rating'] = self._get_rating(item['rating'])
        if 'apk_size' in item:
            item['apk_size'] = _adapt_apk_size(item['apk_size'])
        if 'publish_date' in item:
            item['publish_date'] = _adapt_date_str(item['publish_date'])
        item['description'] = _adapt_desc_str(item.get('description', ''))
        if 'language' in item:
            self._get_detail_info(item)
        return item

    def _get_detail_info(self, item):
        try:
            conn = httplib.HTTPConnection('m.baidu.com')
            url = self._base_url + item['language']
            conn.request("GET", url, headers={"Accept-Language": "zh-CN,zh;q=0.8", "Accept-Charset": "utf-8"})
            response = conn.getresponse()
            data = response.read()
            soup = unicode(data, errors='ignore')
            item['download_link'] = soup.split('downurl=')[1].split(';')[0]
            item['downloads'] = self._get_downloads(soup.split(u'\u4e0b\u8f7d\uff1a')[1].split('+')[0])
        except Exception as e:
            print url
            print e

    def _get_rating(self, rating):
        rating = float(rating[:-1].strip())
        return rating

    def _get_downloads(self, downloads):
        if u'\u5343' in downloads:
            downloads = int(downloads.split(u'\u5343')[0]) * 1000
        elif u'\u4e07' in downloads:
            downloads = int(downloads.split(u'\u4e07')[0]) * 10000
        elif u'\u4ebf' in downloads:
            downloads = int(downloads.split(u'\u4ebf')[0]) * 1000000000
        else:
            downloads = int(downloads)
        return downloads


class OneMobileItemAdapter(ItemAdapter):
    source = '1mobile.com'

    def adapt(self, item):
        ItemAdapter.adapt(self, item)
        if 'publish_date' in item:
            item['publish_date'] = self._get_publish_date(item['publish_date'])
        return item

    def _get_publish_date(self, pubdate):
        return int(datetime.strptime(pubdate, '%Y-%m-%d').strftime('%s'))


class OneMobileAPIItemAdapter(OneMobileItemAdapter):
    source = 'api.1mobile.com'

    def adapt(self, item):
        if 'apk_size' in item:
            item['apk_size'] = _adapt_apk_size(item['apk_size'])
        return OneMobileItemAdapter.adapt(self, item)


class NineOneIphoneItemAdapter(ItemAdapter):

    source = 'ipa.91.com'
    _base_url = 'http://pcx.sj.91.com/soft/all/Controller.ashx?Action=ReadFile&f_id='

    def adapt(self, item):
        super(self.__class__, self).adapt(item)
        if 'version' in item:
            item['version'] = item['version'].split(u'\u7248\u672c\uff1a')[1].strip()
        if 'rating' in item:
            item['rating'] = self._get_rating(item['rating'])
        if 'description' in item:
            self._get_detail_info(item)
        if 'download_link' in item:
            item['download_link'] = self._base_url + item['download_link'].split('(')[1].split(',')[0]
        if 'images' in item:
            item['images'] = ' '.join((item if 'http://' in item else '') for item in item['images'].split("'"))
            item['images_path'] = self._get_images_path(item['images'])
        return item

    def _get_detail_info(self, item):
        info_list = BeautifulSoup(item['description']).findAll(text=True)
        item['description'] = _adapt_desc_str(item.get('screen_support'))
        item['screen_support'] = ''
        pre_info = ''
        for info in info_list:
            if u'\u4e0b\u8f7d\u6b21\u6570\uff1a' in info:
                item['downloads'] = info.split(u'\u4e0b\u8f7d\u6b21\u6570\uff1a')[1].strip()
            if u'\u5f00 \u53d1 \u8005\uff1a' in pre_info:
                item['developer'] = info.strip()
            if u'\u5206\u4eab\u65e5\u671f\uff1a' in info:
                item['publish_date'] = _adapt_date_str(
                    info.split(u'\u5206\u4eab\u65e5\u671f\uff1a')[1].split()[0].strip())
            if u'\u6587\u4ef6\u5927\u5c0f\uff1a' in info:
                item['apk_size'] = _adapt_apk_size(info.split(u'\u6587\u4ef6\u5927\u5c0f\uff1a')[1].strip())
            if u'\u9002\u7528\u56fa\u4ef6\uff1a' in info:
                item['sdk_support'] = info.split(u'\u9002\u7528\u56fa\u4ef6\uff1a')[1].strip()
            pre_info = info

    def _get_rating(self, rating):
        rating = rating.split(',')[1].strip()[0]
        return rating


class NineOneItemAdapter(ItemAdapter):

    source = '91.com'
    _base_url = 'http://mobile.91.com'

    def adapt(self, item):
        super(self.__class__, self).adapt(item)
        if 'rating' in item:
            item['rating'] = self._get_rating(item['rating'])
        if 'description' in item:
            self._get_detail_info(item)
        if 'download_link' in item:
            item['download_link'] = self._base_url + item['download_link']
        return item

    def _get_images_path(self, images):
        images_path = []
        for image in images.split():
            image_guid = hashlib.sha1(image).hexdigest()
            image_path = 'full2/%s/%s/%s.gif' % (image_guid[:1], image_guid[1:3], image_guid)
            images_path.append(image_path)
        return ' '.join(images_path)

    def _get_detail_info(self, item):
        info_list = item['description'].split('<br>')
        for info in info_list:
            if u'\u4eba\u6c14\u6307\u6570\uff1a' in info:
                item['downloads'] = info.split('<span>')[1].split('<')[0].strip()
            if u'\u6240\u5c5e\u5206\u7c7b\uff1a' in info:
                item['category'] = info.split('>')[1].split('<')[0].strip()
            if u'\u4e3b\u9898\u4f5c\u8005\uff1a' in info:
                item['developer'] = info.split(u'\u4e3b\u9898\u4f5c\u8005\uff1a')[1].split('<')[0].strip()
            if u'\u4e0a\u4f20\u65f6\u95f4\uff1a' in info:
                item['publish_date'] = _adapt_date_str(
                    info.split(u'\u4e0a\u4f20\u65f6\u95f4\uff1a')[1].split('<')[0].strip())
            if u'\u4e3b\u9898\u5927\u5c0f\uff1a' in info:
                item['apk_size'] = _adapt_apk_size(
                    info.split(u'\u4e3b\u9898\u5927\u5c0f\uff1a')[1].split('<')[0].strip())
            if u'\u9002\u7528\u673a\u578b\uff1a' in info:
                item['version'] = info.split(u'\u9002\u7528\u673a\u578b\uff1a')[1].split('<')[0].strip()
            if u'\u5173\u952e\u5b57\uff1a' in info:
                soup = BeautifulSoup(info)
                item['screen_support'] = ''.join(soup.findAll(text=True)[1:]).replace(' ', '').replace(u'\u3001', ' ')
            if u'\u4e3b\u9898\u7b80\u4ecb\uff1a' in info:
                item['description'] = info.split(u'\u4e3b\u9898\u7b80\u4ecb\uff1a')[1].strip()

    def _get_rating(self, rating):
        rating = rating.split(',')[1].strip()[0]
        return rating


class NineOneImageItemAdapter(ItemAdapter):

    source = 'image.91.com'
    _base_url = 'http://mobile.91.com'

    def adapt(self, item):
        super(self.__class__, self).adapt(item)
        if 'rating' in item:
            item['rating'] = self._get_rating(item['rating'])
        if 'description' in item:
            self._get_detail_info(item)
        if 'download_link' in item:
            item['download_link'] = self._base_url + item['download_link']
        item['version'] = '1.0'
        return item

    def _get_detail_info(self, item):
        info_list = item['description'].split('<br>')
        for info in info_list:
            if u'\u4eba\u6c14\u6307\u6570\uff1a' in info:
                item['downloads'] = info.split('<span>')[1].split('<')[0].strip()
            if u'\u58c1\u7eb8\u5206\u7c7b\uff1a' in info:
                item['category'] = info.split('>')[1].split('<')[0].strip()
            if u'\u4e0a\u4f20\u65f6\u95f4\uff1a' in info:
                item['publish_date'] = _adapt_date_str(info.split(u'\uff1a')[1].split()[0].strip())
            if u'\u5173\u952e\u5b57\uff1a' in info:
                soup = BeautifulSoup(info)
                item['screen_support'] = ''.join(soup.findAll(text=True)[1:]).replace(' ', '').replace(u'\u3001', ' ')
        item['description'] = ''

    def _get_rating(self, rating):
        rating = rating.split(',')[1].strip()[0]
        return rating


class HiApkItemAdapter(ItemAdapter):

    source = 'hiapk.com'
    _detail_url = "http://apk.hiapk.com/SoftDetails.aspx?action=GetBaseInfo&apkid="
    _rating_dict = {'m_1': 10, 'm_h15': 15, 'm_2': 20, 'm_h25': 25,
                    'm_3': 30, 'm_h35': 35, 'm_4': 40, 'm_h45': 45, 'm_5': 0, }
    _base_url = "http://apk.hiapk.com"

    def adapt(self, item):
        super(self.__class__, self).adapt(item)
#        if 'rating' in item:
#            item['developer'], item['rating'], item['downloads'] = self._get_base_info(item['rating'][0])
        if 'publish_date' in item:
            item['publish_date'] = _adapt_date_str(item.get('publish_date'))
        if 'download_link' in item:
            item['download_link'] = self._base_url + item['download_link']
        if 'apk_size' in item:
            item['apk_size'] = _adapt_apk_size(item['apk_size'])
        item['description'] = _adapt_desc_str(item.get('description'))
        item['update_note'] = _adapt_desc_str(item.get('update_note'))
        return item

    def _get_rating(self, rating):
        if len(rating) == 1:
            return 5

        return self._rating_dict.get(rating[1], 0)


class MumayiItemAdapter(ItemAdapter):

    source = 'mumayi.com'
    _base_url = "http://www.mumayi.com"
    _download_post_url = _base_url + "/plus/disdls.php?aid="

    def adapt(self, item):
        super(self.__class__, self).adapt(item)
        if 'download_link' in item:
            item['downloads'] = self._get_downloads(item['download_link'])
        if 'publish_date' in item:
            item['publish_date'] = _adapt_date_str(item.get('publish_date'))
        if 'rating' in item:
            item['rating'] = float(self._get_rating(item['rating'])) / 10
        if 'name' in item:
            item['name'], item['version'] = self._get_name_version(item['name'])
        if 'sdk_support' in item:
            item['sdk_support'] = item['sdk_support'].strip()
        if 'description' in item:
            item['description'] = item['description'].strip().lstrip(u'\u8f6f\u4ef6\u7b80\u4ecb')
        if 'apk_size' in item:
            item['apk_size'] = _adapt_apk_size(item['apk_size'])
        item['description'] = _adapt_desc_str(item.get('description'))

        return item

    def _get_downloads(self, download_link):
        try:
            if download_link:
                app_id = download_link.split(u'/')[-1]
                # have to pass some data to make it a POST request
                data = urllib.urlencode({'foo': 'bar'})
                response = urllib2.urlopen(self._download_post_url + app_id, data, timeout=15)
                result = response.read()
                return int(result)
        except Exception as e:
            log_error(e)

        return 0

    def _get_rating(self, rating):
        try:
            return int(rating.lstrip(u'rank_now'))
        except Exception as e:
            log_error(e)

        return 0

    def _get_name_version(self, str_compose):
        pattern = re.compile(r'^V[0-9a-zA-Z]+')
        composes = str_compose.strip().split()
        size = len(composes)
        for i in xrange(size - 1, -1, -1):
            index = i
            matcher = pattern.match(composes[i])
            if matcher:
                break

        name = (" ".join(composes[:index if index else 1])).rstrip(' V')
        version = (" ".join(composes[index if index else 1:])).lstrip('V')
        return name, version


class AppChinaItemAdapter(ItemAdapter):

    source = 'appchina.com'
    _base_url = 'http://www.appchina.com'

    def adapt(self, item):
        super(self.__class__, self).adapt(item)
        if 'downloads' in item:
            item['downloads'] = self._get_downloads(item['downloads'].strip(u'\u6b21'))
        if 'publish_date' in item:
            item['publish_date'] = _adapt_date_str(
                item.get('publish_date').replace(u'更新时间：',
                                                 '').replace('\r',
                                                             '').replace('\t',
                                                                         '').replace('\n',
                                                                                     ''))
        if 'rating' in item:
            item['rating'] = item['rating'][1:-1].strip(u'\u5206')
        if 'apk_size' in item:
            item['apk_size'] = _adapt_apk_size(item['apk_size'])
        item['description'] = _adapt_desc_str(item.get('description'))
        unique_source_link(item)
        return item

    def _get_downloads(self, downloads):
        if u'\u5343' in downloads:
            downloads = float(downloads.split(u'\u5343')[0]) * 1000
        elif u'\u4e07' in downloads:
            downloads = float(downloads.split(u'\u4e07')[0]) * 10000
        elif u'\u4ebf' in downloads:
            downloads = float(downloads.split(u'\u4ebf')[0]) * 1000000000
        else:
            downloads = float(downloads)
        return downloads


def unique_source_link(item):
    if item['source_link'].find('?') == -1:
        item['source_link'] = item.get('source_link') + '?' + str(item.get('publish_date', 1))
    else:
        item['source_link'] = item.get('source_link') + '&' + str(item.get('publish_date', 1))


class MyAppItemAdapter(ItemAdapter):

    source = 'myapp.com'
    _base_url = 'http://android.myapp.com'

    def adapt(self, item):
        super(self.__class__, self).adapt(item)
        if 'downloads' in item:
            item['downloads'] = self._get_downloads(item['downloads'].strip(u'\u6b21'))
        if 'publish_date' in item:
            item['publish_date'] = _adapt_date_str(item.get('publish_date'))
        if 'rating' in item:
            item['rating'] = float(item['rating'])
        if 'apk_size' in item:
            item['apk_size'] = _adapt_apk_size(item['apk_size'])
        if 'download_link' in item:
            item['download_link'] = self._base_url + item['download_link']
        item['description'] = _adapt_desc_str(item.get('description'))
        item['update_note'] = _adapt_desc_str(item.get('update_note'))
        unique_source_link(item)
        return item

    def _get_downloads(self, downloads):
        if u'\u5343' in downloads:
            downloads = downloads.split(u'\u5343')[0]
            downloads = float(downloads) if downloads.find(',') == -1 else float(downloads.replace(',', ''))
            downloads = downloads * 1000
        elif u'\u4e07' in downloads:
            downloads = downloads.split(u'\u4e07')[0]
            downloads = float(downloads) if downloads.find(',') == -1 else float(downloads.replace(',', ''))
            downloads = downloads * 10000
        elif u'\u4ebf' in downloads:
            downloads = downloads.split(u'\u4ebf')[0]
            downloads = float(downloads) if downloads.find(',') == -1 else float(downloads.replace(',', ''))
            downloads = downloads * 1000000000
        else:
            downloads = float(downloads) if downloads.find(',') == -1 else float(downloads.replace(',', ''))
        return downloads


class GoApkItemAdapter(ItemAdapter):

    source = 'goapk.com'
    _base_url = 'http://www.goapk.com'
    _download_link_pattern = re.compile(r"opendown\((\d+)\)")

    def adapt(self, item):
        super(self.__class__, self).adapt(item)
        if 'category' in item:
            item['category'] = _adapt_colon_str(item['category'], 1)
        if 'rating' in item:
            item['rating'] = self._get_rating(item['rating'])
        if 'developer' in item:
            item['developer'] = _adapt_colon_str(item['developer'], 1)
        if 'publish_date' in item:
            item['publish_date'] = self._get_publish_date(item['publish_date'])
        if 'downloads' in item:
            item['downloads'] = self._get_downloads(_adapt_colon_str(item['downloads'], 1))
        if 'apk_size' in item:
            item['apk_size'] = _adapt_apk_size(item['apk_size'])
        if 'download_link' in item:
            item['download_link'] = self._get_download_link(item['download_link'])
        if 'version' in item:
            item['version'] = item['version'][1:-1]
        item['description'] = _adapt_desc_str(item.get('description'))

        return item

    def _get_rating(self, rating):
        try:
            if rating:
                rating = float(-int(rating.split()[1][:-3])) / 30
                return rating
        except Exception as e:
            log_error(e)
        return 0

    def _get_publish_date(self, publish_date):
        publish_date = _adapt_date_str(
            _adapt_colon_str(publish_date,
                             1).replace(u'\u5e74',
                                        '-').replace(u'\u6708',
                                                     '-').replace(u'\u65e5',
                                                                  ''))
        return publish_date

    def _get_category(self, category):
        try:
            category = category.replace(u'\u7c7b\u522b:', '').strip()
        except Exception as e:
            log_error(e)
        return category

    def _get_downloads(self, downloads):
        try:
            downloads = downloads.replace(
                u'\u4e0b\u8f7d',
                '').replace(
                u'\u5c0f\u4e8e',
                '').replace(
                u'\u5927\u4e8e',
                '').strip(
            )
            if u'\u4e07\u6b21' in downloads:
                downloads = int(downloads.replace(u'\u4e07\u6b21', '')) * 10000
            elif u'\u5343\u6b21' in downloads:
                downloads = int(downloads.replace(u'\u5343\u6b21', '')) * 1000
            elif u'\u6b21' in downloads:
                downloads = int(downloads.replace(u'\u6b21', ''))
        except Exception as e:
            log_error(e)
        return downloads

    def _get_download_link(self, download_link):
        try:
            if download_link:
                download_link_match = self._download_link_pattern.search(download_link)
                if download_link_match:
                    download_link = '%s/dl_app.php?s=%s' % (self._base_url, download_link_match.group(1))
                return download_link
        except Exception as e:
            log_error(e)
            return download_link


class NDuoAItemAdapter(ItemAdapter):

    source = 'nduoa.com'
    _rating_dict = {'unstared': 0, 'half': 5, 'stared': 10, }
    base_url = 'http://www.nduoa.com'

    def adapt(self, item):
        super(self.__class__, self).adapt(item)
        if 'version' in item:
            item['version'] = item['version'][1:-1]
        if 'apk_size' in item:
            item['apk_size'] = _adapt_apk_size(item['apk_size'])
        if 'rating' in item:
            item['rating'] = self._get_rating(item['rating'].split())
        if 'downloads' in item:
            item['downloads'] = self._get_download(item['downloads'])
        if 'publish_date' in item:
            item['publish_date'] = self._get_publish_date(item['publish_date'])
        if 'download_link' in item:
            item['download_link'] = self.base_url + item['download_link']
        if 'qr_link' in item:
            item['qr_link'] = self.base_url + item['qr_link']
        item['description'] = _adapt_desc_str(item.get('description'))
        return item

    def _get_download(self, download):
        download = download.replace(u'\u6b21\u4e0b\u8f7d', '').replace(u',', '')
        return download

    def _get_rating(self, rating):
        full = rating.count('full')
        half = rating.count('half')
        return full * 1 + half * 0.5

    def _get_version(self, version):
        version = version.replace(u'\uff08', '')
        version = version.replace(u'\uff09', '')
        return version

    def _get_publish_date(self, publish_date):
        publish_date = publish_date.replace(u'\u53d1\u5e03\u4e8e', '')
        if u'\u5929\u524d' in publish_date:
            publish_date = publish_date.replace(u'\u5929\u524d', '')
            publish_date = get_epoch_datetime() - int(publish_date) * 24 * 60 * 60
        elif u'\u5c0f\u65f6\u524d' in publish_date:
            publish_date = publish_date.replace(u'\u5c0f\u65f6\u524d', '')
            publish_date = (get_epoch_datetime() / (60 * 60) - int(publish_date)) * 60 * 60
        return publish_date


def _adapt_date_str(date_str):
    if not date_str:
        return None
    date = datetime.strptime(date_str, "%Y-%m-%d")
    return get_epoch_datetime(date)


def _adapt_colon_str(str, index):
    if u'\uff1a' in str:
        return str.split(u'\uff1a')[index].strip()
    elif ':' in str:
        return str.split(':')[index].strip()
    else:
        return str


def _adapt_desc_str(desc_str):
    if not desc_str:
        return None
    soup = BeautifulSoup(desc_str)
    desc = soup.getText('\n')
    desc = __strip(desc)
    desc = __removeDuplicated(desc)
    desc = __cutTail(desc)
    return desc


def __strip(desc):
        result = ''
        p1 = re.compile(r'[ ]{2,}')
        p2 = re.compile(ur'[-_=　—]{3,}')
        p3 = re.compile(r'[\n]{3,}')
        lines = desc.split('\n')
        lm = len(lines) - 1
        for i in range(0, lm + 1):
            line = lines[i]
            line = line.strip(u' \t\r\n　')
            line = p1.sub('', line)
            line = p2.sub('\n', line)
            if i < lm:
                line += '\n'
            result += line
        result = p3.sub('\n\n', result)
        return result.strip('\n')


def __removeDuplicated(desc):
        result = ''
        lines = desc.split('\n')
        lm = len(lines) - 1
        for i in range(0, lm + 1):
            line = lines[i]
            if i > 0 and line == lines[i - 1]:
                continue
            segs = line.split(' ')
            if len(segs) % 2 == 0:
                mid = len(segs) / 2
                seg1 = ' '.join(segs[0:mid])
                seg2 = ' '.join(segs[mid:])
                if seg1 == seg2:
                    line = seg1
            if i < lm:
                line += '\n'
            result += line
        return result


def __cutTail(desc):
        result = desc.strip('\n')
        if result[-2:] == u'\u6536\u8d77':
            result = result[:-2].strip('\n')
        if result[-12:] == u'\u8be5\u5e94\u7528\u6765\u81ea\u667a\u6c47\u4e91\u5e94\u7528\u5e02\u573a':
            result = result[:-12]
        return result.strip('\n')


def _adapt_apk_size(apk_size):
    if not apk_size:
        return 0
    apk_size = _adapt_colon_str(apk_size, 1)
    if ',' in apk_size:
        apk_size = apk_size.replace(',', '')
    if 'MB' in apk_size:
        apk_size = int(float(apk_size.replace('MB', '').strip()) * 1024 * 1024)
    elif 'KB' in apk_size:
        apk_size = int(float(apk_size.replace('KB', '').strip()) * 1024)
    elif 'GB' in apk_size:
        apk_size = int(float(apk_size.replace('GB', '').strip()) * 1024 * 1024 * 1024)
    elif 'M' in apk_size:
        apk_size = int(float(apk_size.replace('M', '').strip()) * 1024 * 1024)
    elif 'K' in apk_size:
        apk_size = int(float(apk_size.replace('K', '').strip()) * 1024)
    elif 'G' in apk_size:
        apk_size = int(float(apk_size.replace('G', '').strip()) * 1024 * 1024 * 1024)
    return apk_size


class GoogleItemAdapter(ItemAdapter):

    source = 'market.android.com'

    _month_map_dict = {u'January': '01', u'February': '02', u'March': '03', u'April': '04', u'May': '05', u'June': '06',
                       u'July': '07', u'August': '08', u'September': '09', u'October': '10', u'November': '11', u'December': '12'}

    def adapt(self, item):
        super(self.__class__, self).adapt(item)
#        if 'rating' in item:
#            item['rating'] = self._get_rating(item['rating'])
#        if 'downloads' in item:
#            item['downloads'] = self._get_downloads(item['downloads'])
        if 'publish_date' in item:
            item['publish_date'] = self._get_publish_date(item['publish_date'])
        return item

    def _get_rating(self, rating):
        try:
            if rating:
                rating = float(rating)
                rating = int(round(rating * 10))
                if rating < 0:
                    return 0
                elif rating > 50:
                    return 50
                else:
                    return rating
        except Exception as e:
            log_error(e)

        return 0

    def _get_publish_date(self, datetime_str):
        if not datetime_str:
            return None
        datetime_str = datetime_str.replace(u' ', '-')
        datetime_str = datetime_str.replace(u',', '')
        if datetime_str.split("-")[1] in self._month_map_dict:
            datetime_str = datetime_str.split(
                "-")[2] + self._month_map_dict.get(datetime_str.split("-")[1]) + datetime_str.split("-")[0]
        else:
            datetime_str = datetime_str.replace('-', '')
        date = datetime.strptime(datetime_str, "%Y%m%d")
        return get_epoch_datetime(date)

    def _get_downloads(self, downloads_section):

        r = re.compile('^([0-9,]+)[^0-9,]+([0-9,]+)$')
        downloads_min_max = r.match(downloads_section).groups()
        downloads_sum = int(downloads_min_max[0].strip().replace(',', '')) + \
            int(downloads_min_max[1].strip().replace(',', ''))

        return downloads_sum / 2000

GOOGLE_CATEGORY_MAPPING = {
    u'Arcade & Action': u'Action',
    u'Arcade and Action': u'Action',
    u'Adventure': u'Adventure',
    u'Cards & Casino': u'Cards & Casino',
    u'Cards and Casino': u'Cards & Casino',
    u'Casual': u'Casual',
    u'Kids': u'Kids',
    u'Multiplayer': u'Multiplayer',
    u'Brain & Puzzle': u'Puzzles',
    u'Brain and Puzzle': u'Puzzles',
    u'Racing': u'Racing',
    u'Role Playing': u'Role Playing',
    u'Shooter': u'Shooter',
    u'Sports Games': u'Sports Games',
    u'Strategy': u'Strategy',
    u'Tower Defense': u'Tower Defense',
    u'Books & Reference': u'Books & Reference',
    u'Books and Reference': u'Books & Reference',
    u'Business': u'Business',
    u'Comics': u'Comics',
    u'Communication': u'Communication',
    u'Education': u'Education',
    u'Entertainment': u'Entertainment',
    u'Finance': u'Finance',
    u'Health & Fitness': u'Health & Fitness',
    u'Health and Fitness': u'Health & Fitness',
    u'Libraries & Demo': u'Libraries & Demo',
    u'Libraries and Demo': u'Libraries & Demo',
    u'Lifestyle': u'Lifestyle',
    u'Media & Video': u'Media & Video',
    u'Media and Video': u'Media & Video',
    u'Medical': u'Medical',
    u'Music & Audio': u'Music & Audio',
    u'Music and Audio': u'Music & Audio',
    u'News & Magazines': u'News & Magazines',
    u'News and Magazines': u'News & Magazines',
    u'Personalization': u'Personalization',
    u'Personalisation': u'Personalization',
    u'Live Wallpaper': u'Photography',
    u'Photography': u'Photography',
    u'Productivity': u'Productivity',
    u'Shopping': u'Shopping',
    u'Social': u'Social',
    u'Sports': u'Sports',
    u'Widgetses': u'Tools',
    u'Widgets': u'Tools',
    u'Tools': u'Tools',
    u'Transportation': u'Transportation',
    u'Transport': u'Transportation',
    u'Travel & Local': u'Travel & Local',
    u'Travel and Local': u'Travel & Local',
    u'Weather': u'Weather',
    u'Adult': u'Adult',
}


class GooglePlayItemAdapter(GoogleItemAdapter):
    source = 'play.google.com'

    def adapt(self, item):
        ItemAdapter.adapt(self, item)
        if 'publish_date' in item:
            item['publish_date'] = self._get_publish_date(item['publish_date'])
        if 'apk_size' in item:
            item['apk_size'] = _adapt_apk_size(item['apk_size'])
        if 'images' in item:
            item['images'] = ' '.join([url.replace('https', 'http') for url in item['images'].split(' ')])
        if 'downloads' in item:
            item['downloads'] = self._get_downloads(item['downloads'])
        item['icon_path'] = ''
        item['images_path'] = ''
        if 'category' in item:
            item['category'] = GOOGLE_CATEGORY_MAPPING[item['category'].strip()]
        for k, v in item.items():
            if isinstance(v, (list, tuple)):
                item[k] = v[0]
        return item

    def _get_publish_date(self, pubdate):
        pubdate = pubdate.replace('\xe5\xb9\xb4', '-')
        pubdate = pubdate.replace('\xe6\x9c\x88', '-')
        pubdate = pubdate.replace('\xe6\x97\xa5', '')
        return GoogleItemAdapter._get_publish_date(self, pubdate)

