'''
Created on Aug 6, 2011

@author: yan
'''
import time
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from MarketSearch.utils import get_epoch_datetime
from MarketSearch.settings import IDLE_TIME


class DontCloseSpiderExtension(object):

    _spider_idle_time = {}

    def __init__(self):
        dispatcher.connect(self._spider_idle, signal=signals.spider_idle)

    def _spider_idle(self, spider):
        if spider.name not in self._spider_idle_time:
            self._spider_idle_time[spider.name] = get_epoch_datetime()

        last_idle_time = self._spider_idle_time[spider.name]
        now = get_epoch_datetime()
        while IDLE_TIME + last_idle_time > now:
            time.sleep(10)
            now = get_epoch_datetime()

        spider.crawler.queue.append_spider_name(spider.name)
        self._spider_idle_time[spider.name] = now
