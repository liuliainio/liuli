# encoding=utf-8
'''
Created on May 26, 2011

@author: yan
'''
from MarketSearch import service
from MarketSearch.db import market
from MarketSearch.gen.ttypes import Status, LinkStatus, LinkType, Link
from MarketSearch.spiders.linkextractor import SgmlLinkExtractor2
from MarketSearch.utils import log_error, log_info
from scrapy.contrib.loader import XPathItemLoader
from scrapy.contrib.spiders.crawl import CrawlSpider, Rule
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
import httplib
import urllib


_compiled_rules = {}


def on_exception(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise e
    return inner


class AppSpider(CrawlSpider):

    # TODO: for now we treat all these as errors
    handle_httpstatus_list = [403, 404, 500]
    name = ''
    itemloader_class = XPathItemLoader
    scriptprocessor_class = None
    sourcelinkprocessor_class = None
    sourcefilterprocessor_class = None
    redirectprocessor_class = None

    def __init__(self, name=None, **kwarg):
        super(AppSpider, self).__init__(name, **kwarg)

    def start_requests(self):
        if self.name.startswith('update.'):
            links = service.get_update_links(self.get_domain(), 0)
            log_info('will scrape %s links' % len(links))
        else:
            links = service.get_links(self.get_domain(), 0)
            links = list(links) + self.start_urls if isinstance(links, (list, tuple)) else self.start_urls
        #links = ['http://zhushou.360.cn/detail/index/soft_id/148190']
        #links = ['http://www.1mobile.com']
        #links = ['http://www.1mobile.com/voice-changer-calling-192584.html?fr=foot&list=Social&number=10&tab=Download']
        #links = ['https://play.google.com/store/apps/details?id=com.fifa.fifaapp.android']
        for link in links:
            yield self._create_request(link)

    def _create_request(self, link):
        meta = {
            'domain': self.get_domain(),
            'rules': self.get_rule_list(),
            #'dont_redirect' : True,
        }
        callback = self.get_callback(link)
        return Request(url=link, callback=callback, meta=meta)

    def get_callback(self, link):
        '''
        Override this method to assign callback function to request.
        '''
        return self.parse

    def _process_response(self, response, source, type):
        '''
        Returns True if response can be further processed otherwise False.
        '''
        url = response.request.url
        if self.sourcefilterprocessor_class:
            processor = self.sourcefilterprocessor_class()
            url = processor.process(self, url)

        if url is None:
            service.report_status([LinkStatus(url, source, Status.FAIL, type)])
            return False

        if self.sourcelinkprocessor_class:
            processor = self.sourcelinkprocessor_class()
            url = processor.process(url)

        if url is None:
            service.report_status([LinkStatus(url, source, Status.FAIL, type)])
            return False

        if response.status == 200:
            if self.name.startswith('update.'):
                pass
                service.report_update_status([LinkStatus(url, source, Status.SUCCEED, type)])
            else:
                service.report_status([LinkStatus(url, source, Status.SUCCEED, type)])
            return True
        else:
            if self.name.startswith('update.'):
                pass
                service.report_update_status([LinkStatus(url, source, Status.SUCCEED, type)])
            else:
                service.report_status([LinkStatus(url, source, Status.FAIL, type)])
            return False

    @on_exception
    def parse(self, response):
        meta = response.request.meta
        source = meta['domain']
        all_link = []
        url = response.request.url
        if not self._process_response(response, source, LinkType.CATELOG):
            return

        rule_dicts = meta['rules']
        rules = self._get_rules(source, rule_dicts)

        other_links = []
        if source.endswith('hiapk.com'):
            other_links = get_app_list(url)

        for rule in rules:
            links = [l for l in rule.link_extractor.extract_links(response)]
            links.extend(other_links)
            if links and rule.process_links:
                links = rule.process_links(links)

            for link in links:
                if link not in all_link:
                    all_link.append(link)

        if all_link:
            if self.name.startswith('update.'):
                service.report_update_status([LinkStatus(link.url, source, Status.FOUND, rule.link_type)
                                             for link in all_link])
                service.report_update_status([LinkStatus(url, source, Status.SUCCEED, LinkType.CATELOG, len(all_link))])
            else:
                service.report_status([LinkStatus(link.url, source, Status.FOUND, rule.link_type) for link in all_link])
                service.report_status([LinkStatus(url, source, Status.SUCCEED, LinkType.CATELOG, len(all_link))])

        for link in all_link:
            yield self._create_request(link.url)

    @on_exception
    def parse_item(self, response):
        meta = response.request.meta
        source = meta['domain']
        log_info('parse_item_1===========')
        #source = 'appchina.com'
        url = response.request.url
        if self.sourcelinkprocessor_class:
            processor = self.sourcelinkprocessor_class()
            url = processor.process(url)

        if not self._process_response(response, source, LinkType.LEAF):
            service.report_status([LinkStatus(meta['redirect_urls'][0], source, Status.FAIL, type)])
            market.remove_app(url, source)
            log_info('parse_item_2===========')
            return

        if not self.name.startswith('update.') and self.name != 'itunes.apple.com':
            self.parse(response)

        if source.endswith('hiapk.com'):
            body = response.body.replace('</br>', '<p>')
            response = response.replace(body=body)

        if not self.itemloader_class:
            log_info('parse_item_3===========')
            return

        try:
            selector = HtmlXPathSelector(response)
            try:
                loader = self.itemloader_class(selector, response=response)
            except:
                loader = self.itemloader_class(selector)
            # log_info("loader=====%s" %  type(loader))
            loader.add_value('source', source)
            loader.add_value('source_link', url)
        except Exception as e:
            log_info('parse_item_4===========\n%s' %  e)
            log_error(e)
            if self.name.startswith('update.'):
                service.report_update_status([LinkStatus(url, source, Status.FAIL, LinkType.UNKNOWN)])
            else:
                service.report_status([LinkStatus(url, source, Status.FAIL, LinkType.UNKNOWN)])

        log_info('parse_item_5===========' )
        try:
            item = loader.load_item()
            if (self.is_item_valid(item)):
                return item
            else:
                market.remove_app(url, source)
        except Exception as e:
            log_error(e)

    def is_item_valid(self, item, level=0):
        '''
        At least source and source link are present, so an item is valid only it has more attributes loaded.
        '''
        log_info("is_valid===================")
        if level == 0:
            if len(item._values) <= 2:
                return False

        log_info("valid1====================")
        if level == 1:
            # check item count
            if len(item._values) < 9:
                log_info("====1.1====")
                market.report_link(item['source'], 'mass_null', item['source_link'])
                return False

            # check key item
#            if not 'name' in item or not 'version' in item or not 'download_link' in item:
            if not 'name' in item or not 'version' in item \
                    or not 'download_link' in item or not 'publish_date' in item:
                market.report_link(item['source'], 'missing_key', item['source_link'])
                log_info("====1.2====")
                return False

            # check image and icon, just warning, so not return False
            if not 'images' in item or item['images'] == '':
                market.report_link(item['source'], 'missing_image', item['source_link'])
            if not 'icon_link' in item or item['icon_link'] == '':
                market.report_link(item['source'], 'missing_icon', item['source_link'])
        log_info("valid2==================")

        return True

    def process_links(self, links):
        '''
        This is a default link processing implementation.
        '''
        if self.scriptprocessor_class:
            processor = self.scriptprocessor_class()
            links = processor.process(links)

        return links

    def get_rule_list(self):
        '''
        Override this method to provide a list of rules to extract links.
        '''
        return []

    def get_domain(self):
        '''
        Override this method to custom the value of domain, by default is spider's name.
        '''
        if self.name.startswith('update.'):
            return self.name.replace('update.', '')
        elif self.name.startswith('ipad.'):
            return self.name.replace('ipad.', 'ipa.')
        return self.name

    def _compile_rule(self, rule_dict):
        extractor = SgmlLinkExtractor2(allow=rule_dict['allow'], check_url=rule_dict.get('check_url', True))
        rule = Rule(extractor)

        def get_method(method):
            if callable(method):
                return method
            elif isinstance(method, basestring):
                return getattr(self, method, None)
            else:
                return None

        rule.process_links = get_method(rule_dict.get('process_links'))

        # set default link type to leaf
        rule.link_type = rule_dict.get('link_type', LinkType.LEAF)

        return rule

    def _get_rules(self, domain, rule_dicts):
        rules = None
        if domain in _compiled_rules:
            rules = _compiled_rules[domain]
        else:
            rules = []
            for rule_dict in rule_dicts:
                rule = self._compile_rule(rule_dict)
                if rule:
                    rules.append(rule)
            _compiled_rules[domain] = rules
        return rules


def get_app_list(url):
    '''
    var param = {
    "curPageIndex": pageIndex,
    "sortType": sortType,
    "categoryId": categoryId,
    "totaldownloads": totaldownloads,
    "ratings": ratings,
    "commentcount": commentcount,
    "language": language,
    "platform": platform,
    "currentHash": currentHash,
    "isInit": isInit,
    "isPage": isPage
    };
    var url = "/Game.aspx?action=FindGameSoftList";
    $.ajax({
        "type": "POST",
        "url": url,
        "data": param,
        "success": function (result) {
            $("#SoftListBox").html(result);
            sortBoxShowOrHide();
            if (isInit) {
                $(".contidion_box").find(".contidion_span").each(function () {
                    if ($(this).is(".contidion_curr") && $.trim($(this).text()) != "全部") {
                        $(".contidion_line div").eq(0).append("<span class='res_span_p'><label class='result_span'>" + $(this).text() + "</label><label class='iconbg icon_del'></label></span>");
                    }
                });
                contidionhover();
            }
            if (isPage) {
                $('html, body').animate({ scrollTop: 180 }, 500);
            }
        }
    });
    '''
    try:
        list = []
        if url.startswith('http://apk.hiapk.com/apps'):
            base_url = '/App.aspx?action=FindAppSoftList'
        elif url.startswith('http://apk.hiapk.com/games'):
            base_url = '/Game.aspx?action=FindGameSoftList'
        else:
            return list
        currentHash = url.split('#')[1]
        #pageIndex = currentHash.split('_')[0]
        categoryId = url.split('_')[1].split('?')[0]
        post_dict = {
            #'curPageIndex': pageIndex,
            #'sortType':1,
            'categoryId': categoryId,
            #'totaldownloads':0,
            #'ratings':0,
            #'commentcount':0,
            #'language':0,
            #'platform':0,
            'currentHash': currentHash,
            #'isInit':'false',
            #'isPage':'false'
        }
        params = urllib.urlencode(post_dict)
        conn = httplib.HTTPConnection('apk.hiapk.com')
        conn.request("POST", base_url, params, headers={"Content-Type": "application/x-www-form-urlencoded",
                                                        "Origin": "http://apk.hiapk.com",
                                                        "X-Requested-With": "XMLHttpRequest",
                                                        "Referer": "http://apk.hiapk.com",
                                                        "User-Agent":
                                                        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
                                                        })
        response = conn.getresponse()
        data = response.read()
        data_list = data.split('<a')
        for line in data_list:
            if 'http://apk.hiapk.com' in line:
                link = line.split('href="')[1].split('"')[0]
                link = Link(link)
                if link not in list:
                    list.append(link)
    except Exception as e:
        print e
    return list


if __name__ == "__main__":
    get_app_list('http://apk.hiapk.com/apps_49#3_1_0_0_0_0_0')
