#-*- coding: utf-8 -*-
'''
Created on Nov 22, 2013

@author: gmliao
'''
from _mysql_exceptions import MySQLError
from services.core import datasource
from services.core.datasource import BaseDataSource
from services.db import MySQLdbWrapper
from utils.logger import logger
from utils.net import Net
import threading

FIELDS = {
    datasource.FIELD_PACKAGE_NAME: 'package_name',
    datasource.FIELD_VERSION: 'version',
    datasource.FIELD_VERSION_CODE: 'version_code',
    datasource.FIELD_NAME: 'name',
}

_db = threading.local()


def get_db():
    if hasattr(_db, 'db'):
        return _db.db
    else:
        _db.db = MySQLdbWrapper()
        return _db.db


class EstoreDataSource(BaseDataSource):

    NAME = 'estore.com'

    def get_apps_by_packagename(self, packagename_list, fields=None):
        if not isinstance(packagename_list, list):
            packagename_list = [packagename_list]
        url = 'http://estoresrvice.189store.com/api/app/updates2.json'
        param = {
            'clientid': 'kpitest',
            'source': 'kpitest_1',
            'appinfos': '|'.join(['%s:0' % pn for pn in packagename_list]),
            'all_apps': 2,
        }
        header = {'Accept-Encoding': 'gzip,deflate,sdch'}
        json_data = Net.read_json(url, method='post', data=param, header=header)
        ret = []
        ret_packages = set()
        if not fields:
            return ret
        for data in json_data:
            res_data = []
            for f in fields:
                f = FIELDS[f]
                if f not in data:
                    logger.e('key %s not in object: %s' % (f, data))
                    break
                res_data.append(data[f])
                ret_packages.add(data[FIELDS[datasource.FIELD_PACKAGE_NAME]])
            if len(res_data) == len(fields):
                ret.append(res_data)
        logger.e('can not find new version for app: %s' % (set(packagename_list) - ret_packages))
        return ret

    def get_rand_apps(self, fields=None, top_count=20000, rand_count=1000):
        try:
            c = get_db().cursor()
            sql = '''
            select package_name from
                (select distinct package_name from final_app
                where file_type='apk'
                order by cast(downloads as unsigned) desc limit %s) a
            order by rand() limit %s
            '''
            logger.d(sql % (top_count, rand_count))
            c.execute(sql, (top_count, rand_count))
            ret = c.fetchall()
            return ret
        except MySQLError:
            get_db().reconnect()
        finally:
            c.close()


if __name__ == '__main__':
    ds = EstoreDataSource()
    fields = [datasource.FIELD_PACKAGE_NAME, datasource.FIELD_VERSION, datasource.FIELD_VERSION_CODE]
    print ds.get_apps_by_packagename('com.dragon.android.pandaspace', fields)


