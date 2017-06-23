'''
Created on Aug 6, 2011

@author: yan
'''
from scrapy import log
from scrapy.exceptions import IgnoreRequest
from scrapy.contrib.downloadermiddleware.redirect import RedirectMiddleware
from scrapy.contrib.spidermiddleware.httperror import HttpErrorMiddleware, HttpError
from MarketSearch import service
from MarketSearch.gen.ttypes import Status, LinkStatus, LinkType
from MarketSearch.db import market


class RedirectMiddleware(RedirectMiddleware):

    def __init__(self):
        super(RedirectMiddleware, self).__init__()

    def _redirect(self, redirected, request, spider, reason):
        ttl = request.meta.setdefault('redirect_ttl', self.max_redirect_times)
        redirects = request.meta.get('redirect_times', 0) + 1

        if ttl and redirects <= self.max_redirect_times:
            redirected.meta['redirect_times'] = redirects
            redirected.meta['redirect_ttl'] = ttl - 1
            redirected.meta['redirect_urls'] = request.meta.get('redirect_urls', []) + \
                [request.url]
            redirected.dont_filter = request.dont_filter
            redirected.priority = request.priority + self.priority_adjust
            log.msg("Redirecting (%s) to %s from %s" % (reason, redirected, request),
                    spider=spider, level=log.DEBUG)

            if spider.redirectprocessor_class:
                processor = spider.redirectprocessor_class()
                processor.process(redirected, request, spider, reason)

            # report redirect status, usually this link is not valid
            elif reason in [301, 302, 307]:
                source = request.meta['domain']
                if spider.name.startswith('update.'):
                    service.report_update_status([LinkStatus(request.url, source, Status.REDIRECT, LinkType.UNKNOWN)])
                else:
                    service.report_status([LinkStatus(request.url, source, Status.REDIRECT, LinkType.UNKNOWN)])

            return redirected
        else:
            log.msg("Discarding %s: max redirections reached" % request,
                    spider=spider, level=log.DEBUG)
            raise IgnoreRequest


class HttpErrorMiddleware(HttpErrorMiddleware):

    def process_spider_input(self, response, spider):
        # common case
        if 200 <= response.status < 300:
            return
        if 'handle_httpstatus_list' in response.request.meta:
            allowed_statuses = response.request.meta['handle_httpstatus_list']
        else:
            allowed_statuses = getattr(spider, 'handle_httpstatus_list', ())
        if response.status in allowed_statuses:
            return
        source = response.request.meta['domain']
        # report to server
        if spider.name.startswith('update.'):
            service.report_update_status([LinkStatus(response.request.url, source, Status.FAIL, LinkType.UNKNOWN)])
        else:
            service.report_status([LinkStatus(response.request.url, source, Status.FAIL, LinkType.UNKNOWN)])
        # report to monitor
        market.report_link(source, 'http_error', response.request.url, response.status)

    def process_spider_exception(self, response, exception, spider):
        if isinstance(exception, HttpError):
            return []
