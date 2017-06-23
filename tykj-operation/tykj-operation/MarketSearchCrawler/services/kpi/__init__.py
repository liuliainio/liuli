#-*- coding: utf-8 -*-
'''
Created on Nov 22, 2013

@author: gmliao
'''
from services.core import datasource
from services.core.datasource.baidu import BaiduDataSource
from services.core.datasource.estore import EstoreDataSource
from services.core.datasource.wandou import WandoujiaDataSource
from services.core.datasource.zhoushou360 import Zhushou360DataSource
from utils.logger import logger
import sys

reload(sys)
getattr(sys, 'setdefaultencoding')('utf8')


logger.log_file = file('/tmp/estore_quality_kpi.log', 'a')

fields = [datasource.FIELD_PACKAGE_NAME, datasource.FIELD_VERSION_CODE,
          datasource.FIELD_VERSION, datasource.FIELD_NAME]


def kpi1():
    top_count = 20000
    rand_count = 1000
    estore = EstoreDataSource()
    apps0 = estore.get_rand_apps(fields, top_count, rand_count)
    apps = []
    for i in range(0, len(apps0), 50):
        apps_ = estore.get_apps_by_packagename([a[0] for a in apps0[i:i + 50]], fields)
        for a in apps_:
            apps.append(a)
    #apps = [['com.dragon.android.pandaspace', 69, '3.8', u'91手机助手']]
    stores_to_compare = [BaiduDataSource(), WandoujiaDataSource(), Zhushou360DataSource()]
    kpi_res = {}
    for store in stores_to_compare:
        kpi_res[store.NAME] = {
            'source': apps,
            'equal': [],
            'better': [],
            'worse': [],
            'none': [],
        }
        for app in apps:
            try:
                app1 = store.get_app_info_by_packagename(app[0], fields)
            except:
                app1 = None
            if not app1:
                kpi_res[store.NAME]['none'].append(app)
            elif int(app[1]) == int(app1[1]):
                kpi_res[store.NAME]['equal'].append(app)
            elif int(app[1]) > int(app1[1]):
                kpi_res[store.NAME]['better'].append((app, app1))
            elif int(app[1]) < int(app1[1]):
                kpi_res[store.NAME]['worse'].append((app, app1))

    result = []
    result.append('test %s apps from estore.com(random %s of top %s), result: ' % (len(apps), rand_count, top_count))
    result.append(u'(equal: 都有此应用，并且版本一致; better: estore市场应用版本更高;worse: estore市场应用版本更低; none: 对比市场无此应用;)\n')
    result.append('%s\t%s' % ('catetory', '\t'.join([s.NAME for s in stores_to_compare])))
    count_str = 'count\t%s' % ('\t'.join([str(len(kpi_res[s.NAME]['source'])) for s in stores_to_compare]))
    result.append(count_str)
    for k in ['equal', 'better', 'worse', 'none']:
        result.append('%s\t%s' % (k, '\t'.join([str(len(kpi_res[s.NAME][k])) for s in stores_to_compare])))
    result.append('\n%s\t%s' % ('catetory', '\t'.join([s.NAME for s in stores_to_compare])))
    result.append(count_str)
    for k in ['equal', 'better', 'worse', 'none']:
        result.append('%s\t%s' %
                      (k, '\t'.join(['%.2f%%' %
                                     (len(kpi_res[s.NAME][k]) * 100 / (0.0 + len(apps))) for s in stores_to_compare])))

    result.append('\n\n我们市场版本更低的应用: ')
    for s in stores_to_compare:
        result.append('\n%s:' % s.NAME)
        for app, app1 in kpi_res[s.NAME]['worse']:
            result.append(u'%s(%s): %s->%s %s->%s' % (app[3], app[0], app[1], app1[1], app[2], app1[2]))

    print '\n'.join(result)


def kpi2():
    compare_count = 1000
    stores_to_compare = [BaiduDataSource(), WandoujiaDataSource(), Zhushou360DataSource()]
    estore = EstoreDataSource()
    kpi_res = {}
    for store in stores_to_compare:
        try:
            apps = store.get_apps_from_list(compare_count / 2, datasource.LIST_TYPE_SOFT, fields)
        except Exception as e:
            logger.e(e)
            apps = []
        try:
            apps1 = store.get_apps_from_list(compare_count / 2, datasource.LIST_TYPE_GAME, fields)
        except Exception as e:
            logger.e(e)
            apps1 = []
        for a in apps1:
            apps.append(a)
        kpi_res.update({
            store.NAME: {
                'source': apps,
                'equal': [],
                'better': [],
                'worse': [],
                'none': [],
            }
        })

        apps1_dict = {}
        for i in range(0, len(apps), 50):
            apps1 = estore.get_apps_by_packagename([a[0] for a in apps[i:i + 50]], fields)
            for a in apps1:
                apps1_dict[a[0]] = a
        for app in apps:
            app1 = apps1_dict.get(app[0], None)
            if not app1:
                kpi_res[store.NAME]['none'].append(app)
            elif int(app[1]) == int(app1[1]):
                kpi_res[store.NAME]['equal'].append(app)
            elif int(app[1]) > int(app1[1]):
                kpi_res[store.NAME]['better'].append((app, app1))
            elif int(app[1]) < int(app1[1]):
                kpi_res[store.NAME]['worse'].append((app, app1))

    result = []
    result.append('test apps from top list of other market, result: ')
    result.append(u'(equal: 都有此应用，并且版本一致; better: estore市场应用版本更低;worse: estore市场应用版本更高; none: estore市场无此应用;)\n')
    result.append('%s\t%s' % ('catetory', '\t'.join([s.NAME for s in stores_to_compare])))
    count_str = 'count\t%s' % ('\t'.join([str(len(kpi_res[s.NAME]['source'])) for s in stores_to_compare]))
    result.append(count_str)
    for k in ['equal', 'better', 'worse', 'none']:
        result.append('%s\t%s' % (k, '\t'.join([str(len(kpi_res[s.NAME][k])) for s in stores_to_compare])))
    result.append('\n%s\t%s' % ('catetory', '\t'.join([s.NAME for s in stores_to_compare])))
    result.append(count_str)
    for k in ['equal', 'better', 'worse', 'none']:
        str_ = ['%.2f%%' % (len(kpi_res[s.NAME][k]) * 100 / (0.0 + len(kpi_res[s.NAME]['source'])))
                for s in stores_to_compare]
        result.append('%s\t%s' % (k, '\t'.join(str_)))

    result.append('\n\n我们市场版本更低的应用: ')
    for s in stores_to_compare:
        result.append('\n%s:' % s.NAME)
        for app, app1 in kpi_res[s.NAME]['better']:
            result.append(u'%s(%s): %s->%s %s->%s' % (app[3], app[0], app[1], app1[1], app[2], app1[2]))

    result.append(u'\n\n我们市场没有的应用: ')
    for s in stores_to_compare:
        result.append('\n%s:' % s.NAME)
        for app in kpi_res[s.NAME]['none']:
            result.append(u'%s(%s): %s %s' % (app[3], app[0], app[1], app[2]))

    print '\n'.join(result)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'kpi2':
        kpi2()
    else:
        kpi1()







