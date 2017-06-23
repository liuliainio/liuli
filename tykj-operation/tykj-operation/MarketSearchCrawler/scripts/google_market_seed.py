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
_category_list = [u'LIBRARIES_AND_DEMO', u'LIFESTYLE', u'BUSINESS', u'ENTERTAINMENT',
                  u'APP_WIDGETS', u'MEDIA_AND_VIDEO', u'MEDICAL', u'BOOKS_AND_REFERENCE',
                  u'MUSIC_AND_AUDIO', u'SHOPPING', u'CASUAL', u'FINANCE', u'ARCADE', u'COMICS',
                  u'PHOTOGRAPHY', u'BRAIN', u'WEATHER', u'PERSONALIZATION', u'RACING', u'GAME_WIDGETS',
                  u'TRANSPORTATION', u'HEALTH_AND_FITNESS', u'CARDS', u'GAME_WALLPAPER', u'PRODUCTIVITY',
                  u'COMMUNICATION', u'TRAVEL_AND_LOCAL', u'SPORTS', u'APP_WALLPAPER', u'SOCIAL', u'SPORTS_GAMES',
                  u'EDUCATION', u'TOOLS', u'NEWS_AND_MAGAZINES']

_base_url = 'https://play.google.com/store/apps/category/%s/collection/topselling_free?start=%s'
_seed_url_list = []

# check and collect valid url
for category in _category_list:
    index = 0
    error_index = -2
    while True:
        url = _base_url % (category, (index * 24))
        result = check_url(url)
        if result:
            _seed_url_list.append(url)
        else:
            if error_index == index - 1:
                break
            error_index = index
        index = index + 1

# for category in _category_list:
#    for i in range(84):
#        _seed_url_list.append(_base_url % (category, (i * 24)))

# check: insert to db if not exist

_conn = MySQLdb.connect('localhost', 'market', 'P@55word', 'market')
_conn.set_character_set('utf8')
cursor = _conn.cursor()

insert_count = 0
update_count = 0
for seed_url in _seed_url_list:
    # the priority maybe update to failed/missing
    select_sql = "select priority from new_link where source='market.android.com' and link='%s'" % seed_url
    cursor.execute(select_sql)
    results = cursor.fetchall()
    if len(results) == 0:
        insert_sql = "insert new_into link (id, source, link, last_crawl, priority) values ('%s', 'market.android.com', '%s', 1, 10);" % (
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
