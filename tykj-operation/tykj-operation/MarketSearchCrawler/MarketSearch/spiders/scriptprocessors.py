'''
Created on Jun 2, 2011

@author: yan
'''
import re
from scrapy.link import Link
from MarketSearch.spiders.sourcelinkprocessors import BaiduSourceLinkProcessor, NduoaSourceLinkProcessor, AppChinaSourceLinkProcessor, HiApkSourceLinkProcessor, ThreeGGameSourceLinkProcessor, ThreeGSoftSourceLinkProcessor, GoogleSourceLinkProcessor, TripAdvisorSourceLinkProcessor, YoutubeSourceLinkProcessor, YelpSourceLinkProcessor,\
    OneMobileLinkProcessor


class HiApkScriptProcessor():

    source = 'hiapk.com'

    def process(self, links):
        page_links = []
        processor = HiApkSourceLinkProcessor()
        for link in links:
            link.url = processor.process(link.url)
            if link.url:
                page_links.append(link)

        return page_links


class AppChinaScriptProcessor():

    source = 'appchina.com'

    def process(self, links):
        page_links = []
        processor = AppChinaSourceLinkProcessor()
        for link in links:
            link.url = processor.process(link.url)
            if link.url:
                page_links.append(link)

        return page_links


class TripAdvisorScriptProcessor():

    source = 'tripadvisor.com'

    def process(self, links):
        page_links = []
        processor = TripAdvisorSourceLinkProcessor()
        for link in links:
            link.url = processor.process(link.url)
            if link.url:
                page_links.append(link)

        return page_links


class ThreeGGameScriptProcessor():

    source = 'game.3g.cn'

    def process(self, links):
        page_links = []
        processor = ThreeGGameSourceLinkProcessor()
        for link in links:
            link.url = processor.process(link.url)
            if link.url:
                page_links.append(link)

        return page_links


class ThreeGSoftScriptProcessor():

    source = 'soft.3g.cn'

    def process(self, links):
        page_links = []
        processor = ThreeGSoftSourceLinkProcessor()
        for link in links:
            link.url = processor.process(link.url)
            if link.url:
                page_links.append(link)

        return page_links


class GoogleScriptProcessor():

    source = 'market.android.com'

    def process(self, links):
        page_links = []
        processor = GoogleSourceLinkProcessor()
        for link in links:
            link.url = processor.process(link.url)
            if link.url:
                page_links.append(link)

        return page_links


class YoutubeScriptProcessor():

    source = 'youtube.com'

    def process(self, links):
        page_links = []
        processor = YoutubeSourceLinkProcessor()
        for link in links:
            link.url = processor.process(link.url)
            if link.url:
                page_links.append(link)

        return page_links


class YelpScriptProcessor():

    source = 'yelp.com'

    def process(self, links):
        page_links = []
        processor = YelpSourceLinkProcessor()
        for link in links:
            link.url = processor.process(link.url)
            if link.url:
                page_links.append(link)

        return page_links


class NduoaScriptProcessor():

    source = 'nduoa.com'

    def process(self, links):
        page_links = []
        processor = NduoaSourceLinkProcessor()
        for link in links:
            link.url = processor.process(link.url)
            if link.url:
                page_links.append(link)

        return page_links


class BaiduScriptProcessor():

    # source = 'as.baidu.com'
    source = 'shouji.baidu.com'

    def process(self, links):
        page_links = []
        processor = BaiduSourceLinkProcessor()
        for link in links:
            link.url = processor.process(link.url)
            if link.url:
                page_links.append(link)

        return page_links


class OneMobileScriptProcessor():

    source = '1mobile.com'

    def process(self, links):
        page_links = []
        processor = OneMobileLinkProcessor()
        for link in links:
            link.url = processor.process(link.url)
            if link.url:
                page_links.append(link)

        return page_links



