import MySQLdb
from hashlib import md5
import sys

if len(sys.argv) != 3:
    print 'argv error!'
    sys.exit()

source = sys.argv[1]
link = sys.argv[2]

if source not in ['hiapk.com', 'goapk.com', 'nduoa.com', 'mumayi.com',
                  'aimi8.com', 'eoemarket.com', 'market.android.com',
                  'soft.3g.cn']:
    print 'source error'
    sys.exit()

_conn = MySQLdb.connect('localhost', 'market', 'P@55word', 'market')
_conn.set_character_set('utf8')
cursor = _conn.cursor()

hash_key = md5(link).hexdigest().upper()

insert_sql = "insert into link (id, source, link, last_crawl, priority) values " + \
             "('%s', '%s', '%s', 1, 5)" % (hash_key, source, link)

cursor.execute(insert_sql)
_conn.commit()
cursor.close()
