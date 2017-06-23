#!/usr/bin/python
# coding=utf-8
import MySQLdb
import smtplib
import time
import datetime
import os
import pickle
from platform import node


import sys
reload(sys)
getattr(sys, 'setdefaultencoding')('utf-8')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.db import MySQLdbWrapper

_db = MySQLdbWrapper()
cursor = _db.cursor()


results = []
last_date = int(time.time()) - 60 * 60 * 24
date_from = datetime.datetime.strptime(
    (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y%m%d'),
    '%Y%m%d')
date_to = date_from + datetime.timedelta(days=1)
#now = datetime.datetime.now()
#last_date = int(datetime.datetime.strptime(now.strftime('%Y-%m-%d'), '%Y-%m-%d').strftime('%s'))
#sql = 'SELECT a.source,COUNT(DISTINCT b.package_name) AS count_p  FROM app a JOIN final_app b ON a.source_link = b.source_link where a.tag > %d GROUP BY a.source;' % last_date
sql = 'SELECT a.source,COUNT(DISTINCT b.package_name) AS count_p FROM app a JOIN final_app b ON a.source_link = b.source_link where b.created_at between %s and %s GROUP BY a.source;'
cursor.execute(sql, (date_from, date_to))
results_all = cursor.fetchall()

#sql = 'SELECT source,COUNT(distinct package_name) as count_p  FROM ( SELECT a.tag,a.source,b.package_name FROM app a JOIN final_app b ON a.source_link = b.source_link where a.tag>%d GROUP BY package_name HAVING(COUNT(package_name)=1))h  group by source ;' % last_date
sql = '''
select s, count(pn) from
    (select s, pn, ct from
        (SELECT source as s,package_name as pn,created_at as ct FROM final_app where created_at between %s and %s) c
        join final_app d on d.package_name=pn
    group by pn having count(pn) = 1) f
    group by s;
'''
cursor.execute(sql, (date_from, date_to))
results_insert = cursor.fetchall()

sql = 'SELECT a.source,COUNT(DISTINCT b.package_name) AS count_p  FROM app_ios a JOIN final_app b ON a.source_link = b.source_link where a.tag > %d GROUP BY a.source;' % last_date
cursor.execute(sql)
results_ios_all = cursor.fetchall()

sql = 'SELECT source,COUNT(distinct package_name) as count_p  FROM ( SELECT a.tag,a.source,b.package_name FROM app_ios a JOIN final_app b ON a.source_link = b.source_link   where a.tag>%d GROUP BY package_name HAVING(COUNT(package_name)=1))h group by source ;' % last_date
cursor.execute(sql)
results_ios_insert = cursor.fetchall()

results_all = results_all + results_ios_all
results_insert = results_insert + results_ios_insert
results_all_dic = {}
results_insert_dic = {}
for result in results_all:
    results_all_dic[result[0]] = result[1]
for result in results_insert:
    results_insert_dic[result[0]] = result[1]

body = u'''
<b>昨日新增app</b>:<br>
<table>
<tr><td>market</td><td>count</td></tr>
[data]
</table>
'''
data = []
for source in results_all_dic.keys():
    data.append('<tr><td>%s</td><td>%s</td></tr>' % (source, str(results_insert_dic.get(source, 0))))
body = body.replace('[data]', '\n'.join(data))

body += '\n<br>\n'

body += u''''
<b>昨日更新app</b>:<br>
<table>
<tr><td>market</td><td>count</td></tr>
[data]
</table>
'''
data = []

sql = '''
select c_source,count(c_package_name) from
    (select c_source, count(d.id), c_package_name from
        (select source as c_source, package_name as c_package_name, created_at as ct from final_app where created_at between %s and %s ) as c
        join final_app d on c.c_package_name=d.package_name
    group by c.c_package_name having count(d.id) > 1) as e
group by c_source;
'''
update_app_dict = {}
cursor.execute(sql, (date_from, date_to))
for result in cursor.fetchall():
    update_app_dict[result[0]] = result[1]
for source in results_all_dic.keys():
    #data += '<tr><td>%s</td><td>%s</td></tr>' % (source,str(results_all_dic.get(source, 0) - results_insert_dic.get(source, 0)))
    data.append('<tr><td>%s</td><td>%s</td></tr>' % (source, update_app_dict.get(source, 0)))
body = body.replace('[data]', '\n'.join(data))

body += '\n<br>\n'

# unique app count
sql = 'select file_type, count(distinct package_name) as count from final_app group by file_type order by count desc'
cursor.execute(sql)
results = cursor.fetchall()
unique_app_count = {}
for result in results:
    unique_app_count[result[0]] = result[1]

sql = 'select platform, count(distinct package_name) as count from final_app where file_type ="ipa" group by platform order by count desc'
cursor.execute(sql)
results = cursor.fetchall()
for result in results:
    unique_app_count[result[0]] = result[1]

sql = 'select is_break, platform, count(distinct package_name) as count from final_app where file_type ="ipa" group by is_break,platform order by count desc'
cursor.execute(sql)
results = cursor.fetchall()
for result in results:
    unique_app_count[(result[0], result[1])] = result[2]

body += u'<table><tr><td><b>Android应用数量:</b></td><td>%s</td></tr>' % str(unique_app_count['apk'])
body += u'<tr><td><b>iOS应用数量:</b></td><td>%s</td></tr>' % str(unique_app_count['ipa'])
body += u'<tr><td><b>iPhone越狱应用数量:</b></td><td>%s</td></tr>' % str(unique_app_count[(1, 4)])
body += u'<tr><td><b>iPad越狱应用数量:</b></td><td>%s</td></tr>' % str(unique_app_count[(1, 8)])
body += u'<tr><td><b>通用越狱应用数量:</b></td><td>%s</td></tr>' % str(unique_app_count[(1, 12)])
body += u'<tr><td><b>iPhone正版应用数量:</b></td><td>%s</td></tr>' % str(unique_app_count[(0, 4)])
body += u'<tr><td><b>iPad正版应用数量:</b></td><td>%s</td></tr>' % str(unique_app_count[(0, 8)])
body += u'<tr><td><b>通用正版应用数量:</b></td><td>%s</td></tr>' % str(unique_app_count[(0, 12)])
body += u'<tr><td><b>主题数量:</b></td><td>%s</td></tr>' % str(unique_app_count['theme'])
body += u'<tr><td><b>壁纸数量:</b></td><td>%s</td></tr></table>' % str(unique_app_count['wallpaper'])

body += u'<br>'

print 'table statistics: %s,%s,%s,%s' % (datetime.datetime.now().strftime('%Y-%m-%d'), (sum(results_insert_dic.values())), sum(update_app_dict.values()), unique_app_count['apk'])


"""
#app count for each market

sql = 'select source, count(*) as count from app group by source order by count desc'
cursor.execute(sql)
results = cursor.fetchall()
app_count_dict = {}
for result in results:
    app_count_dict[result[0]] = result[1]

#link count for each market
sql = 'select source, count(*) as count from new_link group by source order by count desc'
results = cursor.fetchall()
apk_count_dict = {}
for result in results:
    apk_count_dict[result[0]] = result[1]

#app count for each market

body += u'<table><tr><b><td>市场</td><td>APK数量</td><td>APP数量</td><td>Link数量</td><td>APP数量和Link数量的比率<td></b></tr>'
body += '<tr><td>market</td><td>apk</td><td>app</td><td>link</td><td>app/link</td></tr>[data]</table><br>'
data = ''
sorted_data_list = sorted(app_count_dict.items(), key=lambda d: d[1], reverse=True)
for sorted_data in sorted_data_list:
    source = sorted_data[0]
    if link_count_dict.has_key(source) and app_count_dict.has_key(source) and apk_count_dict.has_key(source):
        data += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (source, str(apk_count_dict[source]), str(app_count_dict[source]), str(link_count_dict[source]), format(float(app_count_dict[source]) / link_count_dict[source], '.2%'))
body = body.replace('[data]', data)

body += '<br>'

#untreated link count
body += u'<table><tr><td><b>未处理链接数</b></td><td></td></tr>'
body += '<tr><td>market</td><td>count</td></tr>[data]</table>'
sql = 'select source, count(*) as count from new_link where last_crawl = 1 group by source order by count desc'
cursor.execute(sql)
results = cursor.fetchall()
data = ''
for result in results:
    data += '<tr><td>%s</td><td>%s</td></tr>' % (result[0], str(result[1]))
body = body.replace('[data]', data)
"""

fromaddr = 'app.search.crawler@gmail.com'
toaddrs = ['kunli@bainainfo.com', 'hlqiao@bainainfo.com', 'yyu@bainainfo.com', 'jli@bainainfo.com', 'yyao@bainainfo.com',
           'gfchen@bainainfo.com', 'jliang@bainainfo.com', 'gmliao@bainainfo.com', 'lyliu@bainainfo.com']
#toaddrs = ['gmliao@bainainfo.com',]
#toaddrs = ['kunli@bainainfo.com']

message = """From: CT APK CRAWLER Statistics
To: %s
MIME-Version: 1.0
Content-type: text/html
Subject: ***monitor report at %s***

%s
""" % (";".join(toaddrs), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), body)

# Credentials
username = 'app.search.crawler'
password = 'youpeng!'

print message.encode('utf8')

# The actual mail send
server = smtplib.SMTP('smtp.gmail.com:587')
server.starttls()
server.login(username, password)
server.sendmail(fromaddr, toaddrs, message.encode('utf8'))
server.quit()


