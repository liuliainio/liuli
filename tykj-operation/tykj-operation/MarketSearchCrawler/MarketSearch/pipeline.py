import hashlib
from scrapy.exceptions import DropItem
from scrapy.contrib.pipeline.images import ImagesPipeline
from scrapy.http import Request
from MarketSearch.db import market
from MarketSearch.db.itemadapters import ItemAdapterFactory
from MarketSearch.utils import log_error, log_info
from MarketSearch.items import CrawledItem, DownloadLinkItem
import traceback

class AppItemAdapterPipeline(object):

    def process_item(self, item, spider):
        try:
            adapter = ItemAdapterFactory.get_itemadapter(item.get('source'))
            if adapter:
                item = adapter.adapt(item)
            return item
        except Exception as e:
            print "------------------------%s" % e
            log_error(e)
            raise DropItem()


class AppItemStorePipeline(object):

    def process_item(self, item, spider):
        log_info("Doing=============")
        try:
            if not hasattr(spider, 'is_item_valid') or spider.is_item_valid(item, 1):
                if isinstance(item, (CrawledItem, )):
                    market.save_app(item, spider.name)
                elif isinstance(item, (DownloadLinkItem, )):
                    market.save_download_link(item)
                return item
            else:
                raise DropItem("invalid item: %s" % item)
        except Exception as e:
            print "------------------------%s" % e
            log_error(e)
            traceback.print_exc()
            raise DropItem()


class AppItemQueueImagePipeline(object):

    def process_item(self, item, spider):
        try:
            icon_dic = {}
            icon_dic['url'] = item['icon_link']
            icon_dic['source_link'] = item['source_link']
            icon_dic['source'] = 'icon'
            market.push_image_url(icon_dic)

            image_dic = {}
            image_dic['url'] = item['images']
            image_dic['source_link'] = item['source_link']
            image_dic['source'] = 'image'
            market.push_image_url(image_dic)

            return item
        except Exception as e:
            log_error(e)
            raise DropItem()


class AppIconPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        if item['icon_link']:
            yield Request(item['icon_link'])

    def image_key(self, url):
        image_guid = hashlib.sha1(url).hexdigest()
        return 'full/%s/%s/%s.jpg' % (image_guid[:1], image_guid[1:3], image_guid)

    def item_completed(self, results, item, info):
        for ok, result in results:
            if not ok:
                log_error("fail to download icon for %s" % item['source_link'])
            else:
                item['icon_path'] = result['path']
            break
        return item


class AppImagesPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        for image in item['images'].split():
            yield Request(image)

    def image_key(self, url):
        image_guid = hashlib.sha1(url).hexdigest()
        return 'full2/%s/%s/%s.jpg' % (image_guid[:1], image_guid[1:3], image_guid)

    def item_completed(self, results, item, info):
        images_path = []
        for ok, result in results:
            if not ok:
                log_error("fail to download image for %s" % item['source_link'])
            else:
                images_path.append(result['path'])
        item['images_path'] = ' '.join(images_path)
        return item
