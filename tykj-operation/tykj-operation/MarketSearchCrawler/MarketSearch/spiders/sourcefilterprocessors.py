'''
Created on Aug 26, 2011

@author: peng
'''
import re


class ThreeGSourceFilterProcessor():

    def process(self, spider, link):
        if link:
            pattern_string = '^http://%s' % spider.name
            pattern = re.compile(pattern_string)
            if pattern.match(link):
                return link
        return None


class AppChinaSourceFilterProcessor():

    def process(self, spider, link):
        if link.startswith('http://www.appchina.com/market/berry/'):
            return None
        else:
            return link
