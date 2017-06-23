'''
Created on Aug 26, 2011

@author: peng
'''
import re


class TripAdvisorSourceLinkProcessor():

    base_url = 'http://www.tripadvisor.com/Hotels'

    def process(self, link):
        return link


class ThreeGGameSourceLinkProcessor():

    base_url = 'http://game.3g.cn/xuan/xuanInfo.aspx'

    def process(self, link):
        if link:
            pattern = re.compile(r'gid=\d+')
            match = pattern.search(link)
            if match and link.startswith(self.base_url):
                link = '%s?%s' % (self.base_url, match.group())
            else:
                link = re.sub('sid=\w+&?', '', link)
                link = re.sub('sortType=\d&?', '', link)
                if link.endswith('&') or link.endswith('?'):
                    link = link[:-1]
            return link
        return None


class ThreeGSoftSourceLinkProcessor():

    base_url = 'http://soft.3g.cn/xuan/xuanInfo.aspx'

    def process(self, link):
        if link:
            id_pattern = re.compile(r'(\?id=|&id=)(\d+)')
            type_pattern = re.compile(r'(\?ftype=|&ftype=)(\d+)')
            page_pattern = re.compile(r'(\?pn=|&pn=)(\d+)')
            id_match = id_pattern.search(link)
            if id_match and link.startswith(self.base_url):
                link = '%s?id=%s' % (self.base_url, id_match.group(2))
            else:
                modified_url = link[:link.find('?')]
                type_match = type_pattern.search(link)
                if type_match:
                    modified_url += '?ftype=%s' % type_match.group(2)
                page_match = page_pattern.search(link)
                if page_match and type_match:
                    modified_url += '&pn=%s' % page_match.group(2)
                elif page_match and not type_match:
                    modified_url += '?pn=%s' % page_match.group(2)
                link = modified_url
            return link
        return None


class YoutubeSourceLinkProcessor():

    base_url = 'http://www.youtube.com/watch'

    def process(self, link):
        if link:
            feature_pattern = re.compile(r'feature=(.*)&|&feature=(.*)')
            feature_match = feature_pattern.search(link)
            if feature_match and link.startswith(self.base_url):
                link = link.replace(feature_match.group(), '')
            return link
        return None


class GoogleSourceLinkProcessor():

    base_url = 'https://play.google.com/store/apps/details'

    def process(self, link):
        if link:
            feature_pattern = re.compile(r'feature=(.*)&|&feature=(.*)|&reviewId=(.*)')
            feature_match = feature_pattern.search(link)
            if feature_match and link.startswith(self.base_url):
                link = link.replace(feature_match.group(), '')
            return link
        return None


class YelpSourceLinkProcessor():

    base_url = 'http://www.yelp.com/biz/'

    def process(self, link):
        if link:
            feature_pattern = re.compile(r'\?q=(.*)|\?sort_by=(.*)')
            feature_match = feature_pattern.search(link)
            if feature_match and link.startswith(self.base_url):
                link = link.replace(feature_match.group(), '')
            return link
        return None


class HiApkSourceLinkProcessor():

    base_url = 'http://static.apk.hiapk.com/html/'

    def process(self, link):
        if link:
            feature_pattern = re.compile(r'\?(.*)')
            feature_match = feature_pattern.search(link)
            if feature_match and link.startswith(self.base_url):
                link = link.replace(feature_match.group(), '')
            return link
        return None


class AppChinaSourceLinkProcessor():

    base_url = 'http://www.appchina.com/app/'

    def process(self, link):
        if link:
            feature_pattern = re.compile(r'\?(.*)')
            feature_match = feature_pattern.search(link)
            if feature_match and link.startswith(self.base_url):
                link = link.replace(feature_match.gourp(), '')
            return link
        return None


class NduoaSourceLinkProcessor():

    base_url = 'http://www.nduoa.com/apk/detail/'

    def process(self, link):
        if link:
            feature_pattern = re.compile(r'\?(.*)')
            feature_match = feature_pattern.search(link)
            if feature_match and link.startswith(self.base_url):
                link = link.replace(feature_match.group(), '')
            return link
        return None


class BaiduSourceLinkProcessor():

    # base_url = 'http://as.baidu.com/'
    base_url = 'http://shouji.baidu.com/'

    def process(self, link):
        if link:
            feature_pattern = re.compile(r'&pre=(.*)|&pos=(.*)|&f=(.*)')
            feature_match = feature_pattern.search(link)
            if feature_match and link.startswith(self.base_url):
                link = link.replace(feature_match.group(), '')
            return link
        return None


class OneMobileLinkProcessor():
    base_url = ['http://www.1mobile.com', 'http://api4.1mobile.com']

    def process(self, link):
        for u in self.base_url:
            if link.startswith(self.base_url):
                return link
            return None






