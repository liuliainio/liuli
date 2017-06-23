#! -*- coding:utf-8 -*-
#!/usr/bin/python
import MySQLdb
from hashlib import md5
import os
import sys


SEEDS = {
    'goapk.com': {
        'url_tpl': [
            'http://www.anzhi.com/sort_1_%d_new.html',
            'http://www.anzhi.com/sort_2_%d_new.html',
        ],
        'range': range(1, 11),
    },
    'hiapk.com': {
        'url_tpl': [
            # 'http://apk.hiapk.com/apps_0?c=%d#%d_3_0_0_0_0_0',
            # 'http://apk.hiapk.com/games_0?x=%d#%d_3_0_0_0_0_0',
            'http://apk.hiapk.com/apps_45_1_%d#%d_1_0_0_0_0_0',
            'http://apk.hiapk.com/apps_49_1_%d#%d_1_0_0_0_0_0',
            'http://apk.hiapk.com/apps_39_1_%d#%d_1_0_0_0_0_0',
            'http://apk.hiapk.com/apps_46_1_%d#%d_1_0_0_0_0_0',
            'http://apk.hiapk.com/apps_42_1_%d#%d_1_0_0_0_0_0',
            'http://apk.hiapk.com/apps_52_1_%d#%d_1_0_0_0_0_0',
            'http://apk.hiapk.com/apps_37_1_%d#%d_1_0_0_0_0_0',
            'http://apk.hiapk.com/apps_35_1_%d#%d_1_0_0_0_0_0',
            'http://apk.hiapk.com/apps_71_1_%d#%d_1_0_0_0_0_0',
            'http://apk.hiapk.com/apps_40_1_%d#%d_1_0_0_0_0_0',
            'http://apk.hiapk.com/games_31_1_%d#%d_1_0_0_0_0_0',
            'http://apk.hiapk.com/games_79_1_%d#%d_1_0_0_0_0_0',
            'http://apk.hiapk.com/games_80_1_%d#%d_1_0_0_0_0_0',
            'http://apk.hiapk.com/games_81_1_%d#%d_1_0_0_0_0_0',
            'http://apk.hiapk.com/games_29_1_%d#%d_1_0_0_0_0_0',
            'http://apk.hiapk.com/games_30_1_%d#%d_1_0_0_0_0_0',
        ],
        'range': range(1, 11),
    },
    'nduoa.com': {
        'url_tpl': [
            'http://www.nduoa.com/cat1?type=2&page=%d',
            'http://www.nduoa.com/cat2?type=2&page=%d',
        ],
        'range': range(1, 11),
    },
    'as.baidu.com': {
        'url_tpl': [
            'http://as.baidu.com/a/software?cid=101&s=1&pn=%d',
            'http://as.baidu.com/a/asgame?cid=102&s=1&pn=%d',
            'http://as.baidu.com/a/software?cid=101&s=2&pn=%d',
            'http://as.baidu.com/a/asgame?cid=102&s=2&pn=%d',
            'http://m.baidu.com/appsrv?action=newcomer&native_api=1&pn=%s&sorttype=game',
            'http://m.baidu.com/appsrv?action=newcomer&native_api=1&pn=%s&sorttype=soft',
            'http://m.baidu.com/appsrv?action=rank&listtype=tophot&native_api=1&pn=%s',
            'http://m.baidu.com/appsrv?action=rank&listtype=topnew&native_api=1&pn=%s',
            'http://m.baidu.com/appsrv?action=rank&listtype=topquick&native_api=1&pn=%s',
            'http://m.baidu.com/appsrv?action=rank&listtype=topscore&native_api=1&pn=%s',
            'http://m.baidu.com/appsrv?action=recommend&native_api=1&pn=%s&sorttype=game',
            'http://m.baidu.com/appsrv?action=recommend&native_api=1&pn=%s&sorttype=recommend',
            'http://m.baidu.com/appsrv?action=recommend&native_api=1&pn=%s&sorttype=soft',
            'http://m.baidu.com/appsrv?action=today&native_api=1&pn=%s',
        ],
        'urls': [
            'http://as.baidu.com/a/rank',
        ],
        'range': range(0, 51),
    },
    'zhushou.360.cn': {
        'url_tpl': [
            'http://zhushou.360.cn/list/index/cid/1/size/all/lang/all/order/download/?page=%d',
            'http://zhushou.360.cn/list/index/cid/2/size/all/lang/all/order/download/?page=%d',
            'http://zhushou.360.cn/list/index/cid/1/size/all/lang/all/order/newest/?page=%d',
            'http://zhushou.360.cn/list/index/cid/2/size/all/lang/all/order/newest/?page=%d',
            'http://zhushou.360.cn/list/index/cid/1/size/all/lang/all/order/rise/?page=%d',
            'http://zhushou.360.cn/list/index/cid/2/size/all/lang/all/order/rise/?page=%d',
            #'http://zhushou.360.cn/list/index/cid/1/size/all/lang/all/order/poll/?page=%d',
            #'http://zhushou.360.cn/list/index/cid/2/size/all/lang/all/order/poll/?page=%d',
        ],
        'range': range(1, 50),
    },
    'wandoujia.com': {
        'url_tpl': [
            "http://www.wandoujia.com/category/app/weekly?page=%d",
            "http://www.wandoujia.com/category/game/weekly?page=%d",
            "http://www.wandoujia.com/tag/动作竞技?page=%d",
            "http://www.wandoujia.com/tag/经营策略?page=%d",
            "http://www.wandoujia.com/tag/角色扮演?page=%d",
            "http://www.wandoujia.com/tag/射击冒险?page=%d",
            "http://www.wandoujia.com/tag/体育竞速?page=%d",
            "http://www.wandoujia.com/tag/休闲益智?page=%d",
            "http://www.wandoujia.com/tag/模拟养成?page=%d",
            "http://www.wandoujia.com/tag/生活?page=%d",
            "http://www.wandoujia.com/tag/社交?page=%d",
            "http://www.wandoujia.com/tag/通信?page=%d",
            "http://www.wandoujia.com/tag/地图?page=%d",
            "http://www.wandoujia.com/tag/拍照?page=%d",
            "http://www.wandoujia.com/tag/影音?page=%d",
            "http://www.wandoujia.com/tag/资讯?page=%d",
            "http://www.wandoujia.com/tag/阅读?page=%d",
            "http://www.wandoujia.com/tag/理财?page=%d",
            "http://www.wandoujia.com/tag/健康?page=%d",
            "http://www.wandoujia.com/tag/词典?page=%d",
            "http://www.wandoujia.com/tag/办公?page=%d",
            "http://www.wandoujia.com/tag/美化?page=%d",
            "http://www.wandoujia.com/tag/系统?page=%d",
            "http://www.wandoujia.com/tag/安全?page=%d",
            "http://www.wandoujia.com/tag/浏览器?page=%d",
            "http://www.wandoujia.com/tag/输入法?page=%d",
        ],
        'range': range(1, 11),
        'url_tpl1': [
            "http://apps.wandoujia.com/api/v1/feeds?opt_fields=adsCursor,data.app.apks.compatible,data.app.apks.incompatibleDetail,data.reason.*,data.app.title,data.app.packageName,data.app.ad,data.app.icons.px78,data.app.installedCountStr,data.app.apks.downloadUrl.url,data.app.apks.bytes,data.app.apks.verified,data.app.apks.versionName,data.app.apks.versionCode,data.app.detailParam,data.app.imprUrl,data.app.stat.weeklyStr,data.app.exclusiveBadge,data.app.apks.md5,data.app.editorComment,data.app.award.issue,data.app.apks.superior,data.app.apks.paidType&area=index&ads_start=0&start=%s&max=30",
            "http://apps.wandoujia.com/api/v1/feeds?opt_fields=adsCursor,data.app.apks.compatible,data.app.apks.incompatibleDetail,data.reason.*,data.app.title,data.app.packageName,data.app.ad,data.app.icons.px78,data.app.installedCountStr,data.app.apks.downloadUrl.url,data.app.apks.bytes,data.app.apks.verified,data.app.apks.versionName,data.app.apks.versionCode,data.app.detailParam,data.app.imprUrl,data.app.stat.weeklyStr,data.app.exclusiveBadge,data.app.apks.md5,data.app.editorComment,data.app.award.issue,data.app.apks.superior,data.app.apks.paidType&area=game&ads_start=0&start=%s&max=30",
            "http://apps.wandoujia.com/api/v1/apps?opt_fields=apks.compatible,apks.incompatibleDetail,title,packageName,ad,icons.px78,installedCountStr,apks.downloadUrl.url,apks.bytes,apks.verified,apks.versionName,apks.versionCode,detailParam,imprUrl,stat.weeklyStr,exclusiveBadge,apks.md5,editorComment,apks.paidType&type=weeklytop&start=%s&max=30",
        ],
        'range1': range(0, 700, 30),
    },
    'appchina.com': {
        'url_tpl': [
            "http://www.appchina.com/category/301/0_0_%d_1_0_0_0.html",
            "http://www.appchina.com/category/302/0_0_%d_1_0_0_0.html",
            "http://www.appchina.com/category/303/0_0_%d_1_0_0_0.html",
            "http://www.appchina.com/category/304/0_0_%d_1_0_0_0.html",
            "http://www.appchina.com/category/305/0_0_%d_1_0_0_0.html",
            "http://www.appchina.com/category/306/0_0_%d_1_0_0_0.html",
            "http://www.appchina.com/category/307/0_0_%d_1_0_0_0.html",
            "http://www.appchina.com/category/308/0_0_%d_1_0_0_0.html",
            "http://www.appchina.com/category/309/0_0_%d_1_0_0_0.html",
            "http://www.appchina.com/category/310/0_0_%d_1_0_0_0.html",
            "http://www.appchina.com/category/311/0_0_%d_1_0_0_0.html",
            "http://www.appchina.com/category/312/0_0_%d_1_0_0_0.html",
            "http://www.appchina.com/category/313/0_0_%d_1_0_0_0.html",
            "http://www.appchina.com/category/314/0_0_%d_1_0_0_0.html",
            "http://www.appchina.com/category/315/0_0_%d_1_0_0_0.html",
            "http://www.appchina.com/category/411/0_0_%d_1_0_0_0.html",
            "http://www.appchina.com/category/412/0_0_%d_1_0_0_0.html",
            "http://www.appchina.com/category/413/0_0_%d_1_0_0_0.html",
            "http://www.appchina.com/category/414/0_0_%d_1_0_0_0.html",
            "http://www.appchina.com/category/415/0_0_%d_1_0_0_0.html",
            "http://www.appchina.com/category/416/0_0_%d_1_0_0_0.html",
            "http://www.appchina.com/category/417/0_0_%d_1_0_0_0.html",
            "http://www.appchina.com/category/418/0_0_%d_1_0_0_0.html",
            "http://www.appchina.com/category/419/0_0_%d_1_0_0_0.html",
            "http://www.appchina.com/category/420/0_0_%d_1_0_0_0.html",
            "http://www.appchina.com/category/421/0_0_%d_1_0_0_0.html",
            "http://www.appchina.com/category/422/0_0_%d_1_0_0_0.html",
            "http://www.appchina.com/category/423/0_0_%d_1_0_0_0.html",
            "http://www.appchina.com/category/424/0_0_%d_1_0_0_0.html",
        ],
        'range': range(0, 5),
    },
    'myapp.com': {
        'url_tpl': [
            'http://android.myapp.com/android/qrycategoryranking_web?cid=101&ranktype=0&pageNo=%d&pageIndex=-1&pageSize=20',
            'http://android.myapp.com/android/qrycategoryranking_web?cid=102&ranktype=0&pageNo=%d&pageIndex=-1&pageSize=20',
            'http://android.myapp.com/android/qrycategoryranking_web?cid=103&ranktype=0&pageNo=%d&pageIndex=-1&pageSize=20',
            'http://android.myapp.com/android/qrycategoryranking_web?cid=104&ranktype=0&pageNo=%d&pageIndex=-1&pageSize=20',
            'http://android.myapp.com/android/qrycategoryranking_web?cid=105&ranktype=0&pageNo=%d&pageIndex=-1&pageSize=20',
            'http://android.myapp.com/android/qrycategoryranking_web?cid=106&ranktype=0&pageNo=%d&pageIndex=-1&pageSize=20',
            'http://android.myapp.com/android/qrycategoryranking_web?cid=107&ranktype=0&pageNo=%d&pageIndex=-1&pageSize=20',
            'http://android.myapp.com/android/qrycategoryranking_web?cid=108&ranktype=0&pageNo=%d&pageIndex=-1&pageSize=20',
            'http://android.myapp.com/android/qrycategoryranking_web?cid=109&ranktype=0&pageNo=%d&pageIndex=-1&pageSize=20',
            'http://android.myapp.com/android/qrycategoryranking_web?cid=110&ranktype=0&pageNo=%d&pageIndex=-1&pageSize=20',
            'http://android.myapp.com/android/qrycategoryranking_web?cid=111&ranktype=0&pageNo=%d&pageIndex=-1&pageSize=20',
            'http://android.myapp.com/android/qrycategoryranking_web?cid=112&ranktype=0&pageNo=%d&pageIndex=-1&pageSize=20',
            'http://android.myapp.com/android/qrycategoryranking_web?cid=113&ranktype=0&pageNo=%d&pageIndex=-1&pageSize=20',
            'http://android.myapp.com/android/qrycategoryranking_web?cid=114&ranktype=0&pageNo=%d&pageIndex=-1&pageSize=20',
            'http://android.myapp.com/android/qrycategoryranking_web?cid=115&ranktype=0&pageNo=%d&pageIndex=-1&pageSize=20',
            'http://android.myapp.com/android/qrycategoryranking_web?cid=116&ranktype=0&pageNo=%d&pageIndex=-1&pageSize=20',
            'http://android.myapp.com/android/qrycategoryranking_web?cid=117&ranktype=0&pageNo=%d&pageIndex=-1&pageSize=20',
            'http://android.myapp.com/android/qrycategoryranking_web?cid=118&ranktype=0&pageNo=%d&pageIndex=-1&pageSize=20',
            'http://android.myapp.com/android/qrycategoryranking_web?cid=119&ranktype=0&pageNo=%d&pageIndex=-1&pageSize=20',
            'http://android.myapp.com/android/qrycategoryranking_web?cid=120&ranktype=0&pageNo=%d&pageIndex=-1&pageSize=20',
            'http://android.myapp.com/android/qrycategoryranking_web?cid=122&ranktype=0&pageNo=%d&pageIndex=-1&pageSize=20',
            'http://android.myapp.com/android/qrycategoryranking_web?cid=121&ranktype=0&pageNo=%d&pageIndex=-1&pageSize=20',
            'http://android.myapp.com/android/qrycategoryranking_web?cid=144&ranktype=0&pageNo=%d&pageIndex=-1&pageSize=20',
            'http://android.myapp.com/android/qrycategoryranking_web?cid=145&ranktype=0&pageNo=%d&pageIndex=-1&pageSize=20',
            'http://android.myapp.com/android/qrycategoryranking_web?cid=146&ranktype=0&pageNo=%d&pageIndex=-1&pageSize=20',
            'http://android.myapp.com/android/qrycategoryranking_web?cid=147&ranktype=0&pageNo=%d&pageIndex=-1&pageSize=20',
            'http://android.myapp.com/android/qrycategoryranking_web?cid=148&ranktype=0&pageNo=%d&pageIndex=-1&pageSize=20',
            'http://android.myapp.com/android/qrycategoryranking_web?cid=149&ranktype=0&pageNo=%d&pageIndex=-1&pageSize=20',
            'http://android.myapp.com/android/qrycategoryranking_web?cid=150&ranktype=0&pageNo=%d&pageIndex=-1&pageSize=20',
            'http://android.myapp.com/android/qrycategoryranking_web?cid=151&ranktype=0&pageNo=%d&pageIndex=-1&pageSize=20',
            'http://android.myapp.com/android/qrycategoryranking_web?cid=152&ranktype=0&pageNo=%d&pageIndex=-1&pageSize=20',
            'http://android.myapp.com/android/qrycategoryranking_web?cid=153&ranktype=0&pageNo=%d&pageIndex=-1&pageSize=20',
        ],
        'range': range(0, 5),
    }
}


def _create_seeds(source, suffix=''):
    for u in SEEDS[source].get('urls', []):
        yield u
    url_tpls = SEEDS[source]['url_tpl' + suffix]
    rge = [i for i in SEEDS[source]['range' + suffix]]
    for url_tpl in url_tpls:
        for i in rge:
            if source == "hiapk.com":
                yield url_tpl % (i, i)
            elif source == "appchina.com":
                yield url_tpl % (i * 18)
            else:
                yield url_tpl % i


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.db import MySQLdbWrapper

_db = MySQLdbWrapper()
cursor = _db.cursor()

insert_count = 0
update_count = 0
for source in SEEDS.keys():
    select_sql = "delete from update_link where source='%s'" % source
    cursor.execute(select_sql)
    seed_list = _create_seeds(source)
    seed_list = [s for s in seed_list]
    if source == 'wandoujia.com':
        seed_list1 = _create_seeds(source, '1')
        for seed in seed_list1:
            seed_list.append(seed)
    for seed_url in seed_list:
        # the priority maybe update to failed/missing
        insert_sql = "insert ignore into update_link (id, source, link, last_crawl, priority) values ('%s', '%s', '%s', 1, 10);" % (
            md5(seed_url).hexdigest().upper(),
            source,
            seed_url)
        cursor.execute(insert_sql)
        _db.conn.commit()
        insert_count += 1

cursor.close()


