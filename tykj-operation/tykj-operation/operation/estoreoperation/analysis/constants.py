#! -*- coding: utf-8 -*-
import logging
import json
import MySQLdb
import datetime
from sqlalchemy import create_engine
from django.conf import settings

logger = logging.getLogger("estoreoperation")

source_mapping = [
    ("featured_", "featured"),
    ("featured", "banner"),
    ("search", "search"),
    ("push", "push"),
    ("10", "push"),
    ("ranking", "banner"),
    ("rank_", "rank"),
    ("rank", "rank"),
    ("category", "category_list"),
    ("developer", "detail_page"),
    ("recommended", "detail_page"),
    ("col_topic_download", "topic"),
    ("column", "topic"),
    ("topic", "topic"),
    ("campaign", "topic"),
    ("focusImage", "banner"),
    ("download", "download"),
    ("quickinstall", "quickinstall"),
    ("SubjectDetail", "topic"),
    ("pay_month", "special_area"),
    ("pay_times", "special_area"),
    ("click_per_pay","special_area"),
    ("click_monthly_pay","special_area"),
    ("reback", "reback"),
    ("webgame_area", "webgame_area"),
    ("webapp","webapp"),
    ("boutique", "CT_area"),
    ("lab", "CT_area"),
    ("default", "other"),
    ("other", "other"),
    ("detail_", "other"),
    ("app_manager_full", "download"),
    ("app_manager_patch", "download"),
    ]


chart_view = {
    "user_chart": {
            u"总留存率": ("product", ["date", "retention_rate"], [u"日期", u"总留存率"], [("retention_rate", 1, ("active_user", "total_user"))]),
            u"用户数": ("product", ["date", "active_user", "total_user"], [u"日期", u"活跃用户数", u"总用户数"], None),
            u"新增用户": ("product", ["date", "new_user"], [u"日期", u"新用户数"], None),
        },
    "product_chart": {
            u"活跃用户人均下载": ("product", ["date", "download_per_user"], [u"日期", u"每活跃用户平均下载"], [("download_per_user", 1, ("downloads", "active_user"))]),
            u"平均停留时间": ("product", ["date", "used_length"], [u"日期", u"使用时长"], None),
            u"总下载数": ("product", ["date", "succeed_download"], [u"日期", u"下载数"], None),
            u"首页访问量": ("featured", ["date", "load", "load_user", "app_click", "app_downloads"],
                    [u"日期", u"加载数", u"使用人数", u"点击量", u"下载量"], None),
            u"榜单访问量": ("topapps", ["date", "load", "load_user", "app_click", "app_downloads"],
                    [u"日期", u"加载数", u"使用人数", u"点击量", u"下载量"], None),
            u"访问来源分布": ("launch_from", ["source", "times"], [u"来源", u"次数"], None),
            u"下载来源": ("download_source", ["source", "times"], [u"下载来源",  u"下载量"], (["source"], [source_mapping])),
        },
    "search_chart": {
            u"访问量": ("search", ["date", "load", "search", "load_user"], [u"日期", u"加载数", u"搜索使用次数", u"使用人数"], None),
            u"推荐热词点击数": ("search", ["date", "keyword_search"], [u"日期", u"推荐热词点击次数"], None),
            u"搜索结果访问量": ("search", ["date", "app_click", "app_downloads"], [u"日期", u"点击数", u"下载数"], None),
            u"人均搜索次数": ("search", ["date", "search_per_user"], [u"日期", u"人均搜索次数"], [("search_per_user", 1, ("search", "load_user"))]),
            u"搜索应用点击率": ("search", ["date", "click_rate"], [u"日期", u"搜索点击率"], [("click_rate", 1, ("app_click", "search"))]),
            u"搜索热词排行榜": ("search_word", ["app_name_id", "times"], [u"搜索词", u"搜索次数"], None),
        },
    "topic_chart": {
            u"专题访问量": ("subject", ["date", "load", "load_user"], [u"日期", u"加载次数", u"使用人数"], None),
            u"专题点击量": ("subject", ["date", "click"], [u"日期", u"专题点击量"], None),
            u"专题应用列表访问量": ("subject", ["date", "app_click", "app_downloads"], [u"日期", u"应用点击量", u"应用下载量"], None),
        },
    "detail_chart": {
            u"加载数": ("detail_page", ["date", "load"], [u"日期", u"加载数"], None),
            u"下载数": ("detail_page", ["date", "app_downloads"], [u"日期", u"下载量"], None),
            u"相关推荐点击量": ("detail_page", ["date", "click_dev", "click_recommended"],
                            [u"日期", u"同开发者应用点击数", u"相关应用点击数"], None),
            u"分享点击数": ("detail_page", ["date", "share"], [u"日期", u"分享数"], None),
            u"来源分布": ("click", ["source", "times"], [u"加载来源", u"次数"], (["source"], [source_mapping])),
        },
    "category_chart": {
            u"首页访问量": ("category", ["date", "load", "load_user"], [u"日期", u"加载次数", u"加载用户数"], None),
        },
    "download_chart": {
            # u"来源分布": (load_download_ranking_data, ["app_name", "app_id",  "source", "times"], [u"应用标题", u"应用ID", u"下载来源",  u"下载量"]),
            u"非应用升级比例": ("full_download_ranking_rate", ["app_name", "app_id", "times", "full_times", "rate"], [u"应用标题", u"应用ID", u"下载量", u"总下载量", u"比例"], [("rate", 1, ("times", "full_times"))]),
            u"下载量": ("download_ranking", ["app_name", "app_id", "times"], [u"应用标题", u"应用ID", u"下载量"], None),
            u"下载来源": ("download_source", ["source", "times"], [u"下载来源",  u"下载量"], (["source"], [source_mapping])),
            u"下载趋势": ("download_trend", ["date", "source", "times"], [u"日期", u"下载来源",  u"下载量"], (["source"], [source_mapping])),
            u"下载成功率": ("product", ["date", "suc_download_rate"], [u"日期", u"下载成功率"], [("suc_download_rate", 1, ("succeed_download", "downloads"))]),
        },
    "featured_chart": {
            u"总下载数": ("featured", ["date", "app_downloads"], [u"日期", u"下载量"], None),
            u"首页访问量": ("featured", ["date", "load"], [u"日期", u"访问量"], None),
            u"人均下载量": ("featured", ["date", "app_downloads_per_user"], [u"日期", u"人均下载量"], \
                    [("app_downloads_per_user", 1, ("app_downloads", "load_user"))]),
            u"各栏目下载量": ("featured_download_detail", ["app_name", "app_id",  "times"], [u"应用标题", u"应用ID", u"下载量"], None),
            u"banner点击量": ("banner", ["date","content", "version", "times"], [u"日期", u"内容", u"版本", u"点击次数"], None),
        },
    "topapps_chart": {
            u"总下载数": ("topapps", ["date", "app_downloads"], [u"日期", u"下载量"], None),
            u"首页访问量": ("topapps", ["date", "load"], [u"日期", u"访问量"], None),
            u"人均下载量": ("topapps", ["date", "app_downloads_per_user"], [u"日期", u"人均下载量"], \
                    [("app_downloads_per_user", 1, ("app_downloads", "load_user"))]),
            u"各栏目下载量": ("topapps_download_detail", ["app_name", "app_id",  "times"], [u"应用标题", u"应用ID", u"下载量"], None),
        },
    "push_chart": {
            u"消息推送": ("push", ["message_id", "load", "app_click", "load_user", "visit_rate", "app_downloads", "download_user", "download_rate", "convert_rate"],
                        [u"推送名称", u"到达数", u"点击量", u"访问人数", u"访问转化率", u"下载量", u"下载人数", u"下载转化率", u"最终转化率"],
                        [("visit_rate", 1, ("load_user", "load")), ("download_rate", 1, ("app_downloads", "app_click")), ("convert_rate", 1, ("app_downloads", "load"))]),
        },
}

CHOICE = False

chart_mapping = {
    "product_chart": {
            'pageName': u'产品图表',
            'choice': CHOICE,
            'chart': 'product_chart',
            'tagClouds': '[{"name":"总下载数","chartType":"line"},{"name":"活跃用户人均下载","chartType":"line"},{"name":"访问来源分布","chartType":"pie"},{"name":"平均停留时间","chartType":"line"},{"name":"首页访问量","chartType":"line","firstSelect":true},{"name":"榜单访问量","chartType":"line"},{"name":"下载来源","chartType":"pie"}]',
        },
    "category_chart": {
            'pageName': u'分类图表',
            'choice': CHOICE,
            'chart': 'category_chart',
            'tagClouds': '[{"name":"首页访问量","chartType":"line","firstSelect":true}]',
        },
    "topic_chart": {
            'pageName': u'专题图表',
            'choice': CHOICE,
            'tagClouds': '[{"name":"专题访问量","chartType":"line","firstSelect":true},{"name":"专题点击量","chartType":"line"},{"name":"专题应用列表访问量","chartType":"line"}]',
        },
    "user_chart": {
            'pageName': u'用户数据图表',
            'choice': CHOICE,
            'tagClouds': '[{"name":"总留存率","chartType":"line"},{"name":"用户数","chartType":"line","firstSelect":true},{"name":"新增用户","chartType":"line"}]',
        },
    "search_chart": {
            'pageName': u'搜索图表',
            'choice': CHOICE,
            'tagClouds': '[{"name":"访问量","chartType":"line","firstSelect":true},{"name":"推荐热词点击数","chartType":"line"},{"name":"搜索结果访问量","chartType":"line"},{"name":"人均搜索次数","chartType":"line"},{"name":"搜索应用点击率","chartType":"line"}, {"name":"搜索热词排行榜","chartType":"no_chart"}]',
        },
    "detail_chart": {
            'pageName': u'详情页面图表',
            'choice': CHOICE,
            'tagClouds': '[{"name":"加载数","chartType":"line","firstSelect":true},{"name":"下载数","chartType":"line"},{"name":"相关推荐点击量","chartType":"line"},{"name":"分享点击数","chartType":"line"},{"name":"来源分布","chartType":"pie"}]',
        },
    "download_chart": {
            'pageName': u'下载量图表',
            'choice': CHOICE,
            'tagClouds': '[{"name":"非应用升级比例","chartType":"no_chart","firstSelect":true},{"name":"下载量","chartType":"no_chart","firstSelect":true,"hasDialog":true},{"name":"下载来源","chartType":"pie"},{"name":"下载趋势","chartType":"area"},{"name":"下载成功率","chartType":"line"}]',
        },
    "featured_chart": {
            'pageName': u'首页图表',
            'choice': CHOICE,
            'chart': 'featured_chart',
            'tagClouds': '[{"name":"总下载数","chartType":"line","firstSelect":false}, {"name":"首页访问量","chartType":"line","firstSelect":true}, {"name":"人均下载量","chartType":"line","firstSelect":false}, {"name":"各栏目下载量","chartType":"no_chart","firstSelect":false,"hasSourceChoices":true},{"name":"banner点击量","chartType":"no_chart","firstSelect":false,"hasSourceChoices":true}]',
        },
    "topapps_chart": {
            'pageName': u'排行图表',
            'choice': CHOICE,
            'chart': 'topapps_chart',
            'tagClouds': '[{"name":"总下载数","chartType":"line","firstSelect":false}, {"name":"首页访问量","chartType":"line","firstSelect":true}, {"name":"人均下载量","chartType":"line","firstSelect":false}, {"name":"各栏目下载量","chartType":"no_chart","firstSelect":false,"hasSourceChoices":true}]',
        },
    "push_chart": {
            'pageName': u'消息推送报表',
            'choice': CHOICE,
            'tagClouds': '[{"name":"消息推送","chartType":"no_chart","firstSelect":true}]',
        },
}

handlers = {
    "banner": {
            "db_handler": "get_banner_data",
            "result_handler": "common_handler"
        },
    "product": {
            "db_handler": "get_product_data",
            "result_handler": "common_handler"
        },
    "search": {
            "db_handler": "get_basic_data",
            "result_handler": "common_handler"
        },
    "featured": {
            "db_handler": "get_basic_data",
            "result_handler": "common_handler"
        },
    "topapps": {
            "db_handler": "get_basic_data",
            "result_handler": "common_handler"
        },
    "category": {
            "db_handler": "get_basic_data",
            "result_handler": "common_handler"
        },
    "subject": {
            "db_handler": "get_basic_data",
            "result_handler": "common_handler"
        },
    "detail_page": {
            "db_handler": "get_basic_data",
            "result_handler": "common_handler"
        },
    "full_download_ranking_rate": {
            "db_handler": "get_noupdate_ranking_rate",
            "result_handler": "appnameid_noupdate_handler"
        },
    "launch_from": {
            "db_handler": "get_rankinglist_data",
            "result_handler": "common_handler"
        },
    "click": {
            "db_handler": "get_rankinglist_data",
            "result_handler": "source_mapping_handler"
        },
    "download_ranking": {
            "db_handler": "get_rankinglist_data",
            "result_handler": "appnameid_handler"
        },
    "download_source": {
            "db_handler": "get_rankinglist_data",
            "result_handler": "source_mapping_handler"
        },
    "download_trend": {
            "db_handler": "get_rankinglist_data",
            "result_handler": "trend_data_handler"
        },
    "search_word": {
            "db_handler": "get_rankinglist_data",
            "result_handler": "common_handler"
        },
    "search_hot_keywords": {
            "db_handler": "get_basic_data",
            "result_handler": "common_handler"
        },
    "featured_download_detail": {
            "db_handler": "get_rankinglist_data",
            "result_handler": "appnameid_handler"
        },
    "topapps_download_detail": {
            "db_handler": "get_rankinglist_data",
            "result_handler": "appnameid_handler"
        },
    "push": {
            "db_handler": "get_push_data",
            "result_handler": "common_handler"
        },
}

translate_mapping = {
    "source": {
        "quickinstall": u"装机必备",
        "download": u"应用更新",
        "category_list": u"分类",
        "topic": u"专题",
        "detail_page": u"详情页面",
        "push": u"消息推送",
        "rank": u"榜单",
        "ranking": u"榜单",
        "search": u"搜索",
        "featured": u"首页",
        "banner": u"banner广告",
        "other": u"其他",
        "start": u"普通启动",
        "update": u"更新提醒",
        "special_area": u"套餐专区",
        "webgame_area": u"游戏专区",
        "webapp":u"绿色应用",
        "CT_area": u"天翼专区",
        "reback": u"回退",
        "featured_a": u"推荐",
        "rank_app": u"应用",
        "rank_game": u"游戏",
        "rank_reading": u"影音",
        "rank_media": u"阅读",
    }
}


set_vars = ["chart_view", "chart_mapping", "source_mapping", "handlers", "translate_mapping"]
conf_db_str = settings.REPORTING_DB_CONF

engine = None
set_done = False
updatetime = None


def get_conf(name):
    global updatetime
    value = globals().get(name)
    if value and updatetime and datetime.datetime.now() - updatetime < datetime.timedelta(seconds=1800):
        return value
    value = getconf_from_db(name)
    globals()[name] = value
    updatetime = datetime.datetime.now()
    return value


def getconf_from_db(name):
    global engine
    var = {}
    if not engine:
        logger.info("engin is None")
        engine = create_engine(conf_db_str, pool_recycle=3600)
    sql = '''select `key`, value from reporting_service_conf where var_name="%s";''' % name
    try:
        values = engine.execute(sql).fetchall()
        for v in values:
            if v:
                try:
                    if v[0]:
                        var[v[0]] = json.loads(v[1])
                    else:
                        var = json.loads(v[1])
                except Exception, e:
                    logger.warn("[%s];%s", str(v), str(e))
    except Exception, e:
        logger.warn(e)
        return {}
    return var


def setconf_to_db(varname, value):
    engine = create_engine(conf_db_str, pool_recycle=3600)
    sql = '''insert into reporting_service_conf(var_name, `key`, value) values("%s", "%s", "%s") on duplicate key update value="%s"'''
    v_tuple = []
    if isinstance(value, dict):
        for key in value.keys():
            # if isinstance(value[key], unicode):
                # value[key] = value[key].encode('utf8')
            v_tuple.append((varname, key, MySQLdb.escape_string(json.dumps(value[key])), \
                    MySQLdb.escape_string(json.dumps(value[key]))))
    else:
        if isinstance(value, unicode):
            value = value.encode('utf8')
        v_tuple.append((varname, "", MySQLdb.escape_string(json.dumps(value)), \
                MySQLdb.escape_string(json.dumps(value))))
    [engine.execute(sql % v) for v in v_tuple]


def set_confs():
    global set_done
    if set_done:
        return
    for varname in set_vars:
        try:
            setconf_to_db(varname, globals().get(varname))
        except Exception, e:
            logger.warn(e, exc_info=True)
    set_done = True

#set_confs()
