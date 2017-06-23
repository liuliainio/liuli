# coding=utf-8

import urllib2
import re
import smtplib
import datetime
from lxml import etree

# 360 zhushou


def get_360():
    url = 'http://www.360.cn/shoujizhushou/update.html'
    c = urllib2.urlopen(url).read()
    doc = etree.HTML(c)
    es = doc.xpath('//h2[@class="tit_3"]')
    version_360 = (es[0].text).encode('iso8859-1').decode('gbk') if len(es) > 0 else 'error occurred!'
    return version_360


# 91 zhushou
def get_91():
    url = 'http://zs.91.com/script/91downloadInfo.js'
    c = urllib2.urlopen(url).read()
    c = c.replace('\r', '')
    c = c.replace('\n', '')
    c = c.replace('\t', '')
    r = re.compile('.*androidJson.*?f_version:"(.*?)".*')
    m = r.match(c)
    version_91 = m.groups()[0] if m and len(m.groups()) > 0 else 'error occurred!'
    return version_91


def get_hiapk():
    url = 'http://apk.hiapk.com/himarket/'
    c = urllib2.urlopen(url).read()
    doc = etree.HTML(c)
    es = doc.xpath('//div[@id="main"]/div/div/div/ul/li')
    version_hiapk = (es[0].text).encode('iso8859-1') if len(es) > 0 else 'error occurred!'
    b = ''
    for a in version_hiapk:
        if hex(ord(a)) != '0xa0':
            b += a
    version_hiapk = b
    return version_hiapk


def get_wandoujia():
    url = 'http://www.wandoujia.com/android'
    c = urllib2.urlopen(url).read()
    c = c.replace('\r', '')
    c = c.replace('\n', '')
    c = c.replace('\t', '')
    r = re.compile('.*/wandoujia-wandoujia_wap_([0-9.]+)\..*')
    m = r.match(c)
    version_wandoujia = m.groups()[0] if m and len(m.groups()) > 0 else 'error occurred!'
    return version_wandoujia


def get_myapp():
    url = 'http://bao.myapp.com/android/'
    c = urllib2.urlopen(url).read()
    doc = etree.HTML(c)
    es = doc.xpath('//div[@class="flash-wrap"]/div[@class="information"]/dl/dd')
    version_myapp = es[0].text if len(es) > 0 else 'error occurred!'
    return version_myapp


def get_baidu():
    return '<img src="http://wap.baidu.com/static/as/images/png/appsearch_android_btn_v1.png"/>'


message_templ = """From: app.search.crawler
To: %s
MIME-Version: 1.0
Content-type: text/html
Subject: check new app version at %s

%s
"""


def sendmail():
    body = u'<table>'
    body += u'<tr><td>360手机助手：</td><td>%s</td></tr>' % get_360()
    body += u'<tr><td>91手机助手：</td><td>%s</td></tr>' % get_91()
    body += u'<tr><td>安卓市场：</td><td>%s</td></tr>' % get_hiapk()
    body += u'<tr><td>豌豆荚：</td><td>%s</td></tr>' % get_wandoujia()
    body += u'<tr><td>应用宝：</td><td>%s</td></tr>' % get_myapp()
    body += u'<tr><td>百度手机助手：</td><td>%s</td></tr>' % get_baidu()
    body += u'</table>'

    fromaddr = 'app.search.crawler@gmail.com'
    toaddr = ['ymli@bainainfo.com']
    toaddr = ['gmliao@bainainfo.com']

    message = message_templ % (';'.join(toaddr), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), body)

    print message.encode('utf8')

    user = 'app.search.crawler'
    password = 'youpeng!'

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(user, password)
    server.sendmail(fromaddr, toaddr, message.encode('utf8'))
    server.quit()

if __name__ == '__main__':
    sendmail()
