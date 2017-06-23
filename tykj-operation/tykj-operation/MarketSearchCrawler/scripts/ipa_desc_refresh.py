# encoding=utf-8
import os
import sys
import simplejson
import MySQLdb
from BeautifulSoup import BeautifulSoup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.db import MySQLdbWrapper

_db = MySQLdbWrapper()


def start_refresh():
    while True:
        ipas = get_ipas()
        if not ipas:
            return
        report_list = []
        for ipa in ipas:
            try:
                if not ipa[1]:
                    desc = ''
                else:
                    for l in ipa[1].split('\n'):
                        if len(l.split(' ')) == 2 and l[0] == l[1]:
                            print l[0]
                        else:
                            print l
#                report_list.append((ipa[0],desc))
            except Exception as e:
                print file
                print e
        report_status(report_list)


def report_status(list):
#    for l in list:
#        try:
#            cursor = _db.cursor()
#            sql = "UPDATE final_app set is_refresh=1, description = %s where id = %s"
#            cursor.execute(sql, (l[1], l[0]))
#            cursor.connection.commit()
#        except MySQLdb.Error,e:
#            print e
#        finally:
#            cursor.close()
    pass


def get_ipas():
    try:
        cursor = _db.cursor()
        sql = "SELECT id,description from app_ios where qr_link is null and source ='ipa.91.com' limit 30"
        cursor.execute(sql)
        results = cursor.fetchall()
        return results
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()


if __name__ == "__main__":
    start_refresh()
