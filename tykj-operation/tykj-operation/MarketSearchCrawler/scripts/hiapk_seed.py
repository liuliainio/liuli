#!/usr/bin/python
import MySQLdb
import smtplib
from hashlib import md5
import urllib2
from urllib2 import Request, urlopen, URLError


def check_url(url):
    req = urllib2.Request(url)
    try:
        urllib2.urlopen(req)
    except Exception as e:
        print e
        return False
    return True

# category list
_app_category_list = [0, 49, 45, 39, 46, 36, 42, 52, 37, 35, 71, 40]
_game_category_list = [0, 31, 79, 80, 81, 29, 30]

_base_url = 'http://apk.hiapk.com/%s_%d?n=%d#%d_1_0_0_0_0_0'
_seed_url_list = []

# check and collect valid url
for category in _app_category_list:
    for i in range(100):
        url = _base_url % ('apps', category, i + 1, i + 1)
        _seed_url_list.append(url)

for category in _game_category_list:
    for i in range(100):
        url = _base_url % ('games', category, i + 1, i + 1)
        _seed_url_list.append(url)

# for category in _category_list:
#    for i in range(84):
#        _seed_url_list.append(_base_url % (category, (i * 24)))

# check: insert to db if not exist

_conn = MySQLdb.connect('localhost', 'root', 'P@55word', 'market')
_conn.set_character_set('utf8')
cursor = _conn.cursor()

insert_count = 0
update_count = 0
for seed_url in _seed_url_list:
    # the priority maybe update to failed/missing
    select_sql = "select priority from new_link where source='hiapk.com' and link='%s'" % seed_url
    cursor.execute(select_sql)
    results = cursor.fetchall()
    if len(results) == 0:
        insert_sql = "insert into new_link (id, source, link, last_crawl, priority) values ('%s', 'hiapk.com', '%s', 1, 10);" % (
            md5(seed_url).hexdigest().upper(),
            seed_url)
        cursor.execute(insert_sql)
        _conn.commit()
        insert_count += 1
    # if priority <> 10, the link has been reported as failed or missing etc. , so update it to normal
    elif results[0][0] != 10:
        update_sql = "update new_link set priority = 10 where link = '%s'" % seed_url
        cursor.execute(update_sql)
        _conn.commit()
        update_count += 1

cursor.close()

# for seed_url in _seed_url_list:
#    item = {'link' : seed_url}
# print "insert into link (id, source, link, last_crawl, priority) values
# ('%s', 'market.android.com', '%s', 1, 10);" %
# (md5(seed_url).hexdigest().upper(), seed_url)

# send mail
body = 'insert count:[%d] <br>' % insert_count
body += 'update_count:[%d] <br>' % update_count

fromaddr = 'app.search.crawler@gmail.com'
toaddrs = ['qpwang@bainainfo.com']

message = """From: APP SEARCH CRAWLER <app.search.crawler@gmail.com>
To: To Person <qpwang@bainainfo.com>
MIME-Version: 1.0
Content-type: text/html
Subject: ***Google Seed Link Report***

%s
""" % body

# Credentials
username = 'app.search.crawler'
password = 'youpeng!'

# The actual mail send
server = smtplib.SMTP('smtp.gmail.com:587')
server.starttls()
server.login(username, password)
server.sendmail(fromaddr, toaddrs, message.encode('utf8'))
server.quit()
