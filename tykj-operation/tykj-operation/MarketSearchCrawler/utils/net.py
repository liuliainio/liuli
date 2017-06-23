#-*- coding: utf-8 -*-
'''
Created on Sep 12, 2013

@author: gmliao
'''
from logger import logger
import re
import requests
import simplejson
import time
import urllib2


class Net(object):

    @staticmethod
    def read_url(url, method='get', data=None, header=None):
        count = 5
        wait = 5
        retry = 0
        ex = None
        while retry < count:
            try:
                if method == 'get':
                    data = data or {}
                    param = '&'.join(['%s=%s' % (k, v) for k, v in data.items()])
                    if url.find('?') != -1:
                        url = '%s&%s' % (url, param)
                    else:
                        url = '%s%s' % (url, param)
                    res = requests.get(url, headers=header or {}).content
                else:
                    res = requests.post(url, data or {}, headers=header or {}).content
                return res
            except Exception as e:
                logger.w("request for url: %s, failed. will retry after %s seconds." % (url, wait))
                retry = retry + 1
                time.sleep(wait)
                ex = e
        raise ex

    @staticmethod
    def read_json(url, func=None, method='get', data=None, header=None):
        count = 5
        retry = 0
        ex = None
        urlresponse = None
        while retry < count:
            try:
                urlresponse = Net.read_url(url, method, data, header)
                if func is not None:
                    urlresponse = func(urlresponse)
                res = simplejson.loads(urlresponse)
                return res
            except Exception as e:
                logger.w(u"parse json for url: %s, failed. jsonstr: %s." % (url, urlresponse))
                retry = retry + 1
                ex = e
        raise ex

    @staticmethod
    def download(url, filepath):
        f = None
        try:
            f = file(filepath, 'w')
            f.write(requests.get(url).content)
            logger.i('download file from `%s` to `%s` success.' % (url, filepath))
        except Exception as e:
            logger.e('download file from `%s` to `%s` fail: %s' % (url, filepath, e))
            raise e
        finally:
            if f:
                f.close()

    @staticmethod
    def get_redirect_url1(url):
        try:
            req = urllib2.Request(url)
            res = urllib2.urlopen(req)
            return res.geturl()
        except Exception as e:
            return '%s' % e

    @staticmethod
    def get_redirect_url(url):
        req = urllib2.Request(url)
        res = urllib2.urlopen(req)
        return res.geturl()


if __name__ == '__main__':
    furls = set()
    fapkpaths = set()
    for url in file('apk_to_delete'):
        furl = Net.get_redirect_url1(url)
        if furl.find('HTTP Error 404') == -1:
            furls.add(furl)
            r = re.compile('.*(vol[0-9]+)/.*p=(.*)$')
            m = r.match(furl)
            if m:
                fapkpaths.add('%s/%s' % tuple(m.groups()))
            else:
                r = re.compile('.*(static.*)$')
                m = r.match(furl)
                if m:
                    fapkpaths.add('%s' % tuple(m.groups()))
                else:
                    r = re.compile('.*(vol[0-9]+/.*\.apk)$')
                    m = r.match(furl)
                    if m:
                        fapkpaths.add('%s' % tuple(m.groups()))
                    else:
                        print 'can not parse url: %s' % furl
    for u in furls:
        print u
    for u in fapkpaths:
        print u


