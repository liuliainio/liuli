'''
Created on Jun 1, 2011

@author: yan
'''
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor, BaseSgmlLinkExtractor, _matches, _is_valid_url
from scrapy.utils.url import canonicalize_url, url_is_from_any_domain


class SgmlLinkExtractor2(SgmlLinkExtractor):

    def __init__(self, allow=(), deny = (), allow_domains = (), deny_domains = (), restrict_xpaths = (),
                 tags = ('a', 'area'), attrs = ('href'), canonicalize = True, unique = True, process_value = None, check_url = True):
        # Add check_url parameter
        self.check_url = check_url

        SgmlLinkExtractor.__init__(
            self, allow=allow, deny=deny, allow_domains=allow_domains, deny_domains=deny_domains, restrict_xpaths=restrict_xpaths,
            tags=tags, attrs=attrs, canonicalize=canonicalize, unique=unique, process_value=process_value)

    def _process_links(self, links):
        links = [link for link in links if not self.check_url or _is_valid_url(link.url)]

        if self.allow_res:
            links = [link for link in links if _matches(link.url, self.allow_res)]
        if self.deny_res:
            links = [link for link in links if not _matches(link.url, self.deny_res)]
        if self.allow_domains:
            links = [link for link in links if url_is_from_any_domain(link.url, self.allow_domains)]
        if self.deny_domains:
            links = [link for link in links if not url_is_from_any_domain(link.url, self.deny_domains)]

        if self.canonicalize:
            for link in links:
                link.url = canonicalize_url(link.url)

        links = BaseSgmlLinkExtractor._process_links(self, links)
        return links
