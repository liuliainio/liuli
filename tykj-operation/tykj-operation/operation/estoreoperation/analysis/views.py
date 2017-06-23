#! -*- coding: utf-8 -*-
import logging
import hashlib
import itertools
import datetime as org_datetime
from decimal import Decimal
from datetime import date, datetime, timedelta
import time
try:
    from collections import OrderedDict as ordict
except ImportError:
    try:
        from ordereddict import OrderedDict as ordict
    except ImportError:
        raise
from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.views.static import serve
from django.http import HttpResponse
from estoreoperation.utils import json_response
from reporting.db import get_reporting_store
from constants import get_conf
from export_file import export_file, export_filepath, export_file_format, export_simple_excel, export_special_excel
from list_analysis import get_basic_download, get_basic_search

FREEZE_DATE = "2013-04-11"

filename_mapping = {
    "csv": "data.csv",
    "xls": "data.xls",
}

export_filename = filename_mapping[export_file_format]

logger = logging.getLogger("estoreoperation")

DB_CONF = {
    'reporting': {
        'conn_str': settings.REPORTING_DB_CONF
    }}

store = get_reporting_store(DB_CONF)


def safe_div(a, b):
    if float(b) == 0.0:
        return 0
    else:
        return float(a) / float(b)


def get_request_params(request):
    global store
    GET = request.GET

    if 'product' in GET:
        DB_CONF['reporting']['conn_str'] = settings.REPORTING_DB_CONF if GET['product'] == 'reset' \
                else settings.REPORTING_DB_CONF.replace("reporting_appstore", 'reporting')
        store = get_reporting_store(DB_CONF)

    logger.debug("mysql string reset to %s", DB_CONF['reporting']['conn_str'])

    if ("start" in GET and "end" in GET):
        start_date = GET["start"]
        end_date = GET["end"]
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        except TypeError, e:
            logger.exception('Invaild start/end date value, start_date: %s, end_date: %s, error: %s' % (start_date, end_date, e))
    else:
        today = datetime.today()
        start_date = (today + timedelta(days=-7)).date()
        end_date = (today + timedelta(days=-1)).date()

    ret = {
        'chart_name': GET.get('chart_name'),
        'report_name': GET.get('report_name'),
        'start_date': start_date,
        'end_date': end_date,
        'search_word': GET.get('search_word'),
        'app_name_id': '%s_%s' % (GET['app_name'], GET['app_id']) if GET.get("app_name") and GET.get("app_id") else None,
        'versions': GET['versions'].split(',') if 'versions' in GET else [],
        'sources': GET['source'].split(',') if 'source' in GET else [],
    }
    logger.debug(ret)
    return ret


def translate(report_name, datas, *args, **kwargs):
    translate_mapping = get_conf("translate_mapping")
    if report_name not in (u"访问来源分布", u"下载来源", u"来源分布"):
        return datas
    results = []
    for data in datas:
        if set(data.keys()) & set(translate_mapping.keys()):
            for key in data.keys():
                if key in translate_mapping.keys():
                    data[key] = translate_mapping[key].get(data[key], data[key])
        results.append(data)
    return results


def before(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return d1 < d2


def generate_downloadid(column_list, start_date, end_date, appkey=None):
    st = ''
    for s in column_list:
        st += s
    if appkey and isinstance(appkey, str):
        st += appkey
    return hashlib.md5(st + str(start_date) + str(end_date)).hexdigest()


def write_result(reportname2column, params, callback=()):
    ret = []
    report_name = params['report_name']
    if report_name in reportname2column.keys():
        downloadid = generate_downloadid(reportname2column[report_name][1],
                params['start_date'], params['end_date'])
        ret.append({"downloadid": downloadid})
        data_handler = reportname2column[report_name]
        datas = get_data(data_handler[0], store, params, data_handler[3])
        if data_handler[0] == 'download_trend':
            ret.extend(datas)
        else:
            for func in callback:
                datas = func(report_name, datas, start_date=params['start_date'])
            for i, column_name in enumerate(data_handler[1]):
                v = {"name": column_name if not data_handler[2] else data_handler[2][i]}
                v["data"] = [data.get(column_name) for data in datas]
                ret.append(v)
        export_file(ret)
    return ret


def dict_div(data, *l):
    return safe_div(data.get(l[0], 0), data.get(l[1], 0))


def dict_minus(data, *l):
    return data.get(l[0], 0) - data.get(l[1], 0)


def common_handler(datas, handler_args):
    columns = [data.get('name') for data in datas.column_descriptions]
    caculater_mapping = {0: dict_minus, 1: dict_div}

    ret = []
    for data in datas:
        v = {}
        for key, value in zip(columns, data):
            if isinstance(value, Decimal):
                value = int(value)
            if key == 'app_name_id':
                value = value.decode('utf-8')
            v[key] = value
        if 'date' in v:
            v['date'] = v['date'].strftime('%Y-%m-%d')
        if handler_args:
            for args in handler_args:
                v[args[0]] = caculater_mapping[args[1]](v, *args[2])
        ret.append(v)
    return ret

def appnameid_noupdate_handler(datas, handler_args):
    columns = ['app_name_id','times','full_times','rate']
    caculater_mapping = {0: dict_minus, 1: dict_div}
    ret = []
    for data in datas[:200]:
        v = {}
        for key, value in zip(columns, data):
            if isinstance(value, Decimal):
                value = int(value)
            if key == 'app_name_id':
                value = value.decode('utf-8')
            v[key] = value
        try:
            infos = v['app_name_id'].split('_')
            if len(infos) < 2:
                app_name = infos[0]
                app_id = 0
            elif len(infos) > 2:
                app_name = '_'.join(infos[:-1])
                app_id = infos[-1]
            else:
                app_name, app_id = infos[0], infos[1]
        except ValueError:
            app_name = v['app_name_id']
            app_id = 0
        v['app_name'] = app_name
        v['app_id'] = app_id

        if handler_args:
            for args in handler_args:
                v[args[0]] = caculater_mapping[args[1]](v, *args[2])
        ret.append(v)
    return ret

def appnameid_handler(datas, handler_args):
    columns = [data.get('name') for data in datas.column_descriptions]
    ret = []
    for data in datas[:200]:
        v = {}
        for key, value in zip(columns, data):
            if isinstance(value, Decimal):
                value = int(value)
            if key == 'app_name_id':
                value = value.decode('utf-8')
            v[key] = value
        try:
            infos = v['app_name_id'].split('_')
            if len(infos) < 2:
                app_name = infos[0]
                app_id = 0
            elif len(infos) > 2:
                app_name = '_'.join(infos[:-1])
                app_id = infos[-1]
            else:
                app_name, app_id = infos[0], infos[1]
        except ValueError:
            app_name = v['app_name_id']
            app_id = 0
        v['app_name'] = app_name
        v['app_id'] = app_id
        ret.append(v)
    return ret


def combin_row(data, vectors=["source"]):
    keyfunc = lambda row: str([str(row[v]) for v in vectors])
    data.sort(key=keyfunc)
    records = []
    for _, rows in itertools.groupby(data, keyfunc):
        rows = [r for r in rows]
        rows[0]["times"] = sum(int(r["times"]) for r in rows)
        records.append(rows[0])
    return records


def mapping_vector_name(mapping, name):
    #use orderdict
    #http://stackoverflow.com/questions/5629023/key-order-in-python-dicionaries
    if not isinstance(mapping, list):
        return name
    for key in ordict(mapping).keys():
        if key in name:
            return ordict(mapping)[key]
    return name


def source_mapping_handler(datas, handler_args):
    res = []
    columns = [data.get('name') for data in datas.column_descriptions]
    for data in datas:
        v = {}
        for key, value in zip(columns, data):
            if isinstance(value, Decimal):
                value = int(value)
            v[key] = value
        if handler_args:
            for i, vector in enumerate(handler_args[0]):
                v[vector] = mapping_vector_name(handler_args[1][i], v[vector])
        res.append(v)
    return combin_row(res, vectors=handler_args[0])


def convert_trend_data(results):
    dates = sorted(list(set([r['date'] for r in results])))
    sources = list(set([r['source'] for r in results]))
    final_results = [{'name': u'日期', 'data': dates}]
    values = {}
    source_mapping = get_conf("translate_mapping")['source']

    for r in results:
        key = r['date'] + '_' + r['source']
        if key in values.keys():
            values[key] += int(r['times'])
        else:
            values[key] = int(r['times'])
    for source in sources:
        value_list = []
        for d in dates:
            value_list.append(values.get(d + '_' + source, 0))
        final_results.append({'name': source_mapping.get(source, source), 'data': value_list})

    return final_results


def trend_data_handler(datas, handler_args):
    res = []
    columns = [data.get('name') for data in datas.column_descriptions]
    for i, data in enumerate(datas):
        v = {}
        for key, value in zip(columns, data):
            if isinstance(value, Decimal):
                value = int(value)
            elif isinstance(value, date):
                value = str(value)
            v[key] = value
        if handler_args:
            for i, vector in enumerate(handler_args[0]):
                v[vector] = mapping_vector_name(handler_args[1][i], v[vector])
        res.append(v)
    return convert_trend_data(res)


def get_data(reportname, store, params, handler_args):
    handlers = get_conf("handlers")

    datas = store.__getattribute__(handlers[reportname]["db_handler"])(reportname, params,
                            versions=params['versions'], appkeylist=None)
    return globals().get(handlers[reportname]["result_handler"])(datas, handler_args)


#@permission_required('auth.view_search_reporting', login_url='../../admin')
#@staff_member_required
@login_required
@json_response
def reporting_data(request):
    chart_view = get_conf("chart_view")
    params = get_request_params(request)
    if not params['report_name'] or not params['chart_name'] or \
        params['chart_name'] not in chart_view.keys():
        return []
    return write_result(chart_view[params['chart_name']], params, callback=(translate, ))

times = 0
appkeys = []
versions = []
featured_download_sources = ['latest', 'recommend']
rank_download_sources = []


def get_all_appkeys():
    global appkeys, times
    times += 1
    if not appkeys or times % 1000 == 0:
        appkeys = store.get_all_appkeys()
    return appkeys


def get_all_versions():
    global versions, times
    times += 1
    if not versions or times % 1000 == 0:
        versions = store.get_all_versions()
    return versions


def get_sources(reportname):
    global featured_download_sources, rank_download_sources, times
    times += 1
    translate_mapping = get_conf("translate_mapping")
    reportname_mappings = {
            u"首页图表": (featured_download_sources, 'featured_'),
            u"排行图表": (rank_download_sources, 'rank_'),
        }
    sources = reportname_mappings[reportname][0]

    if not sources or times % 1000 == 0:
        sources = store.get_ranking_sources(reportname_mappings[reportname][1])
        final_sources = [[s, translate_mapping['source'][s]] for s in sources if translate_mapping['source'].get(s,None)]
        sources = final_sources

    return sources


@login_required
@json_response
def get_choices(request):
    reportname = request.GET.get("reportname")
    if not reportname:
        return []

    if reportname in (u"产品图表", u"分类图表", u"下载量图表", u"专题图表",
        u"用户数据图表", u"搜索图表", u"详情页面图表", u"消息推送图表"):
        return [{"display": True, "display_name": u"版本", "parametername": "versions",
            "data": get_all_versions()}]
    elif reportname in (u"首页图表", u"排行图表",):
        return [
            {"display": True, "display_name": u"版本", "parametername": "versions", "data": get_all_versions()},
            {"display": True, "display_name": u"栏目", "parametername": "source", "data": get_sources(reportname)},
        ]
    return []


@login_required
def loadfile(request):
    downloadid = request.GET.get("downloadid")
    if not downloadid:
        return HttpResponse("Missed downloadid")
    path = export_filename + '.' + downloadid
    return serve(request, path, export_filepath)


@login_required
def reporting_chart_page(request, name):
    chart_mapping = get_conf("chart_mapping")
    if name in chart_mapping:
        chart_mapping[name]['chart'] = name
        return render_to_response('reporting.html', chart_mapping[name], context_instance=RequestContext(request))


def is_valid_date(str):
    try:
        time.strptime(str, "%Y-%m-%d")
        return True
    except:
        return False


@login_required
def export_list_analysis(request):
    from_date = request.GET.get('date', '').strip()
    if from_date and is_valid_date(from_date):
        real_date = from_date
    else:
        real_date = org_datetime.date.today()
    return render_to_response('export.html', {'from_date': str(real_date)}, context_instance=RequestContext(request))



@login_required
def export_file_analysis(request):
    params = {}
    from_date = request.GET.get('date', '').strip()
    if from_date and is_valid_date(from_date):
        real_date = from_date
    else:
        real_date = org_datetime.date.today()

    params['start_date'] = str(real_date)
    params['end_date'] = str(real_date)
    list_type = request.GET.get('list_type', '').strip()
    list_detail = request.GET.get('list_detail', '').strip()
    action = request.GET.get('action', '').strip()
    params['list_type'] = list_type
    params['list_detail'] = list_detail
    params['action'] = action

    row_header = []
    if list_type == 'search':
        ret_data = get_basic_search(params)
        row_header = ['id', 'name', 'total_times']
    else:
        ret_data = get_basic_download(params)

    if ret_data:
        unique_id = hashlib.md5(str(real_date) + str(list_type) + str(list_detail)).hexdigest()
        filename = 'data%s.xls' % unique_id
        if row_header:
            export_special_excel(filename, ret_data, names=row_header)
        else:
            export_simple_excel(filename, ret_data)
        return serve(request, filename, export_filepath)
    else:
        return HttpResponse('Sorry, Fail to get detail.')


def print_all(data):
    ret = ''
    for d in data:
        s = 'id:%s,order:%s,name:%s,detail_times:%s,outer_times:%s<br/>' % (d['id'],d['order'],d['name'],d['detail_times'],d['outer_times'])
        ret += s
    return ret
