'''
Created on Aug 26, 2011

@author: peng
'''
import re
from MarketSearch import service
from MarketSearch.gen.ttypes import Status, LinkStatus, LinkType


class ThreeGRedirectProcessor():

    def process(self, redirected, request, spider, reason):
        pattern_string = '^http://%s' % spider.name
        pattern = re.compile(pattern_string)

        redirected_url = redirected.url
        redirected_match = pattern.match(redirected_url)
        request_match = pattern.match(request.url)
        if redirected_match is None and request_match:
            if spider.sourcelinkprocessor_class:
                processor = spider.sourcelinkprocessor_class()
                request_url = processor.process(request.url)
            service.report_status([LinkStatus(request_url, spider.name, Status.FAIL, LinkType.LEAF)])


class RedirectShoujiBaiduProcessor():
    
    # hlqiao. 20140818
    def process(self, redirected, request, spider, reason):
        # print "type"
        # return redirected.replace(callback=spider.redirected_downlink)
        pass
