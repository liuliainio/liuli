#-*- coding: utf-8 -*-
'''
Created on Dec 11, 2013

@author: gmliao
'''
import sys
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
import urllib2
import requests


class RequestHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
        print 'GET %s' % self.path
        p = self.path
        if p.find('?') == -1:
            return SimpleHTTPRequestHandler.do_GET(self)
        params = dict(p0.split('=') for p0 in p[p.find('?') + 1:].split('&'))
        url = params['url']
        start = params.get('start', None)
        end = params.get('end', None)
        method = params.get('method', None)
        r = requests.get(urllib2.unquote(url), headers={'Range': 'bytes=%s-%s' % (start, end)})
        self.wfile.write(r.content)
        print 'download end for url: %s, start=%s, end=%s' % (url, start, end)


HandlerClass = RequestHandler
ServerClass = BaseHTTPServer.HTTPServer
Protocol = "HTTP/1.0"


if sys.argv[1:]:
    port = int(sys.argv[1])
else:
    port = 13000
server_address = ('0.0.0.0', port)

HandlerClass.protocol_version = Protocol
httpd = ServerClass(server_address, HandlerClass)

sa = httpd.socket.getsockname()
print "Serving HTTP on", sa[0], "port", sa[1], "..."
httpd.serve_forever()
