# -*- coding: utf-8 -*-
import os
import re
import urllib
import logging
from dateutil import parser
from django.conf import settings
from django.utils import simplejson
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseNotModified
from django.views.decorators.http import require_GET, require_POST
from estorecore.servemodels.app import AppMongodbStorage, APP_FIELDS_LIST_MEDIUM, APPLIST_ITEM_TYPE_APPDETAIL
from estorecore.servemodels.user import UserMongodbStorage
from estorecore.servemodels.update import UpdateMongodbStorage
from estorecore.servemodels.patch import PatchMongodbStorage
from estorecore.utils import friendly_size
from estoreservice.utils.utils import json_response, combine_url, append_icon_host, build_img_url, to_int_array, build_apk_url
from estoreservice.api.errors import parameter_error, resource_not_exist
from estoreservice.api.utils import get_parameter_GET, get_parameter_POST, get_parameter_META
from estorecore.servemodels.search import SearchMongodbStorage
from estorecore.db import timestamp_utc_now
from estoreservice.api.actions.reviewactions import PostReviewAction, QueryReviewAction

logger = logging.getLogger('estoreservice')

CATEGORY_ID_RESERVED_NEWAPPS = 10
CATEGORY_ID_RESERVED_HOTPS = 11

app_db = AppMongodbStorage(settings.MONGODB_CONF)
user_db = UserMongodbStorage(settings.MONGODB_CONF)
update_db = UpdateMongodbStorage(settings.MONGODB_CONF)
search_db = SearchMongodbStorage(settings.MONGODB_CONF)
patch_db = PatchMongodbStorage(settings.MONGODB_CONF)

RECOMMENDS_ORDERS = app_db.query_recommend_types()
#APP_LISTS =  app_db.query_app_lists()

AREA_TABLE = {
    str(app_db.AREA_RECOMMEND): app_db.AREA_RECOMMEND,
    str(app_db.AREA_TOP): app_db.AREA_TOP,
    str(app_db.AREA_CATEGORY): app_db.AREA_CATEGORY,
    'recommend': app_db.AREA_RECOMMEND,
    'top': app_db.AREA_TOP,
    'category': app_db.AREA_CATEGORY,
}

CATEGORY_APPS_ORDERS = {
    'downloads': app_db.CATEGORY_APPS_ORDER_DOWNLOADS,
    'download': app_db.CATEGORY_APPS_ORDER_DOWNLOADS,
    'rating': app_db.CATEGORY_APPS_ORDER_RATING,
    'time': app_db.CATEGORY_APPS_ORDER_TIME,

    'poll': app_db.CATEGORY_APPS_RANK_RATING,
    'rankrate': app_db.CATEGORY_APPS_RANK_RATING,
    'rankspiking': app_db.CATEGORY_APPS_RANK_SPIKING,
    'ranknew': app_db.CATEGORY_APPS_RANK_NEW,
    'rankdownload': app_db.CATEGORY_APPS_ORDER_DOWNLOADS,
    'order': app_db.CATEGORY_APPS_ORDER_ORDER,
}


def _convert_order(order, order_dicts={}):
    if order not in order_dicts:
        raise Exception(
            'order %s does not in order_dicts %s' %
            (order, order_dicts))
    return order_dicts[order]

from functools import partial
_convert_recommends_order = partial(
    _convert_order,
    order_dicts=RECOMMENDS_ORDERS)
_convert_category_apps_order = partial(
    _convert_order,
    order_dicts=CATEGORY_APPS_ORDERS)
_convert_area = partial(_convert_order, order_dicts=AREA_TABLE)


def _result_info(results, formatter=lambda x: x['id'] if 'id' in x else ''):
    if isinstance(results, dict) and 'results' in results:
        if results['results']:
            return [formatter(r) for r in results['results']]
    if isinstance(results, list):
        if results and 'id' in results[0]:
            return [formatter(r) for r in results]
    return results


def gen_small_preview_icon_url(url):
    if not url:
        return url
    if not url.startswith('img'):
        return url
    return 's_' + url


def is_app_supported(app, os, screen_size):
    if os:
        if 'min_sdk_version' in app and app['min_sdk_version'] is not None:
            if app['min_sdk_version'] > os:
                return False
        if 'max_sdk_version' in app and app['max_sdk_version'] is not None:
            if app['max_sdk_version'] < os:
                return False

    # TODO: screen size check

    return True


def _app_post_process(apps, with_details=False,
                      related_apps_count=0, os=None, screen_size=None):
    is_list = True
    if not isinstance(apps, list):
        apps = [apps]
        is_list = False

    if is_list:
        # it's ok to set os=None and screen_size=None, if you put the filter
        # logic in the db selection
        if os or screen_size:
            apps = [
                app for app in apps if is_app_supported(
                    app,
                    os,
                    screen_size)]

    if with_details:
        apps = app_db.get_apps_with_details(apps)

    if related_apps_count:
        apps = app_db.get_related_apps_for_list(apps, related_apps_count)
        for app in apps:
            if 'related_apps' in app:
                append_icon_host(app['related_apps'])

    for app in apps:
        if 'download_count' in app:
            if app['download_count'] >= 10000:
                # TODO: localization
                app['display_download_count'] = u'%d万' % (
                    app['download_count'] / 10000)
            else:
                app['display_download_count'] = str(app['download_count'])
        if 'preview_icon_urls' in app:
            app['small_preview_icon_urls'] = ','.join(
                [build_img_url(
                    gen_small_preview_icon_url(img)) for img in re.split(',| ',
                                                                         app['preview_icon_urls'])])
            app['preview_icon_urls'] = ','.join(
                [build_img_url(img) for img in re.split(',| ', app['preview_icon_urls'])])
        if 'apps' in app:    # for subject items
            app['apps'] = append_icon_host(app['apps'])
        if 'promote' in app:
            del app['promote']

    append_icon_host(apps)

    return apps if is_list else apps[0]


def app_post_process(apps, with_details=False,
                     related_apps_count=0, os=None, screen_size=None):
    if not apps:
        return apps
    if isinstance(apps, dict) and 'results' in apps:
        apps['results'] = _app_post_process(
            apps['results'],
            with_details,
            related_apps_count,
            os,
            screen_size)
    else:
        apps = _app_post_process(
            apps,
            with_details,
            related_apps_count,
            os,
            screen_size)
    return apps


def get_app(app_id, package_name, platform=1, jailbreak=False):
    app = None
    if app_id:
        app = app_db.get_info(int(app_id))
    elif package_name:
        app = app_db.get_app_by_package(
            package_name,
            platform=platform,
            jailbreak=jailbreak)
    return app


@require_GET
@json_response
def app_categories(request):
    client_id = get_parameter_GET(request, 'clientid')
    parent_categories = get_parameter_GET(
        request,
        'p_cate_id',
        convert_func=to_int_array)
    start_index = get_parameter_GET(request, 'start_index', convert_func=int)
    count = get_parameter_GET(request, 'count', convert_func=int)
    with_total = get_parameter_GET(
        request,
        'wt',
        convert_func=bool,
        required=False)
    for q in (client_id, parent_categories, start_index, count):
        if isinstance(q, HttpResponse):    # convert failed
            return q

    return (
        append_icon_host(
            app_db.query_categories(
                parent_categories=parent_categories,
                start_index=start_index,
                count=count,
                with_total=with_total))
    )


@require_GET
@json_response
def app_category_apps(request):
    client_id = get_parameter_GET(request, 'clientid')
    cate_id = get_parameter_GET(request, 'cate_id', convert_func=to_int_array)
    cate_level = get_parameter_GET(
        request,
        'catelevel',
        convert_func=int,
        default=1)  # 0: top category, 1: sub category
    os = get_parameter_GET(
        request,
        'os',
        required=False,
        convert_func=int,
        default=None)
    screen_size = get_parameter_GET(request, 'screensize', required=False)
    platform = get_parameter_GET(
        request,
        'platform',
        convert_func=int,
        required=False,
        default=1)
    app_type = get_parameter_GET(
        request,
        'app_type',
        convert_func=int,
        required=False,
        default=None)
    order = get_parameter_GET(
        request,
        'order',
        convert_func=_convert_category_apps_order,
        default='downloads')
    start_index = get_parameter_GET(
        request,
        'start_index',
        convert_func=int,
        default=0)
    count = get_parameter_GET(request, 'count', convert_func=int, default=10)
    with_total = get_parameter_GET(
        request,
        'wt',
        convert_func=bool,
        required=False)
    with_details = get_parameter_GET(
        request,
        'details',
        convert_func=bool,
        required=False)
    related_apps_count = get_parameter_GET(
        request,
        'relatedappscount',
        convert_func=int,
        required=False)

    for q in (client_id, cate_id, order, start_index, count):
        if isinstance(q, HttpResponse):    # convert failed
            return q

    results = app_db.query_category_apps(
        category_id=cate_id,
        cate_level=cate_level,
        platform=platform,
        app_type=app_type,
        start_index=start_index,
        count=count,
        order=order,
        with_total=with_total)
    logger.info('app_category_apps, client_id=%s, results=%s'
                % (str(client_id), _result_info(results)))

    return (
        app_post_process(
            results,
            with_details=with_details,
            related_apps_count=related_apps_count,
            os=os,
            screen_size=screen_size)
    )


def _app_list_mapping(cate_id, recommend_type, focus_image=False):
    app_list_id = None
    if not focus_image:
        if not recommend_type:
            # hardcore , for migration , we have to do this.
            if cate_id == 14334:
                app_list_id = 1
            elif cate_id == 14357:
                app_list_id = 2
        else:
            cate_mapping = {
                None: {
                    'base': 3,
                    'mapping': (10, 11, 13),
                },
                14387: {
                    'base': 6,
                    'mapping': (10, 11, 12, 14, 15, 16),
                },
                14401: {
                    'base': 12,
                    'mapping': (10, 12),
                },
                14357: {
                    'base': 14,
                    'mapping': (10, 11, 12, 17),
                },
            }
            if cate_id in cate_mapping:
                base = cate_mapping[cate_id]['base']
                mapping = cate_mapping[cate_id]['mapping']
                for i, c in enumerate(mapping):
                    if recommend_type == c:
                        app_list_id = base + i
                        break
    else:
        app_list_id = 22
    return app_list_id


@require_GET
@json_response
def app_list_apps(request):
    client_id = get_parameter_GET(request, 'clientid')
    source = get_parameter_GET(request, 'source')
    #app_list_id = get_parameter_GET(request, 'list_id', convert_func=_convert_app_list)
    app_list_id = get_parameter_GET(request, 'list_id')
    banner_list_id = get_parameter_GET(
        request,
        'bannerlistid',
        required=False,
        default=0)
    start_index = get_parameter_GET(
        request,
        'start_index',
        convert_func=int,
        required=False,
        default=0)
    count = get_parameter_GET(
        request,
        'count',
        convert_func=int,
        required=False,
        default=10)
    with_total = get_parameter_GET(
        request,
        'wt',
        convert_func=bool,
        required=False)
    with_details = get_parameter_GET(
        request,
        'details',
        convert_func=int,
        required=False)
    related_apps_count = get_parameter_GET(
        request,
        'relatedappscount',
        convert_func=int,
        required=False)
    for q in (client_id, source, app_list_id, start_index, count):
        if isinstance(q, HttpResponse):    # convert failed
            return q

    results = app_db.query_apps_from_list(
        app_list_id=app_list_id,
        start_index=start_index,
        count=count,
        with_total=with_total)
    if start_index == 0 and banner_list_id:
        banners = app_db.query_apps_from_list(
            app_list_id=banner_list_id,
            start_index=start_index,
            count=count,
            with_total=False)
        for banner in banners:
            banner['is_big_banner'] = '1'
        if with_total:
            banners += results['results']
            results['results'] = banners
        else:
            results = banners + results

    if with_details:
        apps = results['results'] if with_total else results
        apps = append_icon_host(apps)
        for app in apps:
            if app.get('type', -1) == APPLIST_ITEM_TYPE_APPDETAIL:
                app['soft_large_logo_url'] = app['icon_url']
                del app['icon_url']
                if 'description' in app:
                    del app['description']

    logger.info(
        'app_list_apps, client_id=%s, results=%s' %
        (client_id, _result_info(results)))

    return (
        app_post_process(
            results,
            with_details=with_details,
            related_apps_count=related_apps_count)
    )


@require_GET
@json_response
def app_category_focus_images(request):
    client_id = get_parameter_GET(request, 'clientid')
    source = get_parameter_GET(request, 'source')
    cate_id = get_parameter_GET(
        request,
        'cate_id',
        convert_func=int,
        required=False)
    recommend_type = get_parameter_GET(
        request,
        'recommend_type',
        convert_func=_convert_recommends_order,
        required=False)
    area = get_parameter_GET(request, 'area', convert_func=_convert_area)
    start_index = get_parameter_GET(request, 'start_index', convert_func=int)
    count = get_parameter_GET(request, 'count', convert_func=int)
    with_total = get_parameter_GET(
        request,
        'wt',
        convert_func=bool,
        required=False)
    with_details = get_parameter_GET(
        request,
        'details',
        convert_func=bool,
        required=False)
    related_apps_count = get_parameter_GET(
        request,
        'relatedappscount',
        convert_func=int,
        required=False)
    for q in (client_id, cate_id, recommend_type, area, start_index, count):
        if isinstance(q, HttpResponse):    # convert failed
            return q
    if bool(cate_id) == bool(recommend_type):
        return (
            parameter_error(
                request,
                "[(cate_id, recommend_type), one and only one is expected]")
        )

    app_list_id = _app_list_mapping(None, None, focus_image=True)
    results = app_db.query_apps_from_list(
        app_list_id=app_list_id,
        start_index=start_index,
        count=count,
        with_total=with_total)

    # SPECIAL CODE for diandian
    if with_details:
        apps = results['results'] if with_total else results
        apps = append_icon_host(apps)
        for app in apps:
            app['id'] = int(app['attr'])
            app['download_url'] = combine_url(
                settings.SERVICE_HOST, 'api/app/download/app.json?clientid=%s&source=%s&app_id=%d' %
                (client_id, source, app['id']))
            app['soft_large_logo_url'] = app['icon_url']
            app['market_id'] = 'diandian'
            del app['icon_url']
            if 'description' in app:
                del app['description']

        results = app_post_process(
            results,
            with_details=with_details,
            related_apps_count=related_apps_count)
    else:
        results = append_icon_host(results)

    return results


@require_GET
@json_response
def app_category_tops(request):
    client_id = get_parameter_GET(request, 'clientid')
    cate_id = get_parameter_GET(
        request,
        'cate_id',
        convert_func=int)    # TODO: validator
    start_index = get_parameter_GET(request, 'start_index', convert_func=int)
    count = get_parameter_GET(request, 'count', convert_func=int)
    with_total = get_parameter_GET(
        request,
        'wt',
        convert_func=bool,
        required=False)
    with_details = get_parameter_GET(
        request,
        'details',
        convert_func=int,
        required=False)
    related_apps_count = get_parameter_GET(
        request,
        'relatedappscount',
        convert_func=int,
        required=False)
    for q in (client_id, cate_id, start_index, count):
        if isinstance(q, HttpResponse):    # convert failed
            return q

    app_list_id = _app_list_mapping(cate_id, None)
    if not app_list_id:
        return []
    results = app_db.query_apps_from_list(
        app_list_id=app_list_id,
        start_index=start_index,
        count=count,
        with_total=with_total,
        fields=APP_FIELDS_LIST_MEDIUM)
    logger.info('app_category_tops, client_id=%s, results=%s'
                % (client_id, _result_info(results)))

    return (
        app_post_process(
            results,
            with_details=with_details,
            related_apps_count=related_apps_count)
    )


@require_GET
@json_response
def app_recommends(request):
    client_id = get_parameter_GET(request, 'clientid')
    recommend_type = get_parameter_GET(
        request,
        'type',
        convert_func=_convert_recommends_order)
    start_index = get_parameter_GET(request, 'start_index', convert_func=int)
    count = get_parameter_GET(request, 'count', convert_func=int)
    cate_id = get_parameter_GET(
        request,
        'cate_id',
        convert_func=int,
        required=False)
    with_total = get_parameter_GET(
        request,
        'wt',
        convert_func=bool,
        required=False)
    with_details = get_parameter_GET(
        request,
        'details',
        convert_func=bool,
        required=False)
    related_apps_count = get_parameter_GET(
        request,
        'relatedappscount',
        convert_func=int,
        required=False)
    for q in (client_id, recommend_type, start_index, count):
        if isinstance(q, HttpResponse):    # convert failed
            return q

    app_list_id = _app_list_mapping(cate_id, recommend_type)
    if not app_list_id:
        return []
    results = app_db.query_apps_from_list(
        app_list_id=app_list_id,
        start_index=start_index,
        count=count,
        with_total=with_total)
    logger.info('app_recommends, client_id=%s, type=%s, cate_id=%s, results=%s'
                % (client_id, str(recommend_type), str(cate_id), _result_info(results)))

    return (
        app_post_process(
            results,
            with_details=with_details,
            related_apps_count=related_apps_count)
    )


@require_GET
@json_response
def app_subjects(request):
    client_id = get_parameter_GET(request, 'clientid')
    app_list_id = get_parameter_GET(request, 'app_list_id', convert_func=int)
    start_index = get_parameter_GET(request, 'start_index', convert_func=int)
    count = get_parameter_GET(request, 'count', convert_func=int)
    with_total = get_parameter_GET(
        request,
        'wt',
        convert_func=bool,
        required=False)
    for q in (client_id, app_list_id, start_index, count):
        if isinstance(q, HttpResponse):    # convert failed
            return q

    results = app_db.query_subjects(
        app_list_id,
        start_index=start_index,
        count=count,
        with_total=with_total)
    logger.info('app_subjects, client_id=%s, results=%s'
                % (client_id, _result_info(results)))

    return append_icon_host(results)


def _format_subject_apps(results):
    app_list = []
    for item in results:
        app_list.extend(item['apps'])

    return app_list


@require_GET
@json_response
def app_subject_apps(request, version):
    client_id = get_parameter_GET(request, 'clientid')
    subject_id = get_parameter_GET(request, 'subject_id', convert_func=int)
    start_index = get_parameter_GET(
        request,
        'start_index',
        convert_func=int,
        required=False,
        default=0)
    count = get_parameter_GET(
        request,
        'count',
        convert_func=int,
        required=False,
        default=10)
    with_total = get_parameter_GET(
        request,
        'wt',
        convert_func=bool,
        required=False)
    for q in (client_id, subject_id, start_index, count):
        if isinstance(q, HttpResponse):    # convert failed
            return q

    results = app_db.query_subject_apps(
        subject_id,
        start_index=start_index,
        count=count,
        with_total=with_total)
    for result in results:
        if 'apps' in result:
            result['apps'] = app_post_process(result['apps'])
    if version == 1:
        results = _format_subject_apps(results)
    logger.info(
        'app_subject_apps, version=%s, client_id=%s, results=%s' %
        (version, client_id, _result_info(results)))

    return app_post_process(results)


@require_GET
@json_response
def app_info(request):
    client_id = get_parameter_GET(request, 'clientid')
    source = get_parameter_GET(request, 'source', required=False, default='')
    app_id = get_parameter_GET(request, 'app_id', required=False, default=None)
    package_name = get_parameter_GET(request, 'packagename', required=False)
    related_apps_count = get_parameter_GET(
        request,
        'relatedappscount',
        convert_func=int,
        required=False,
        default=8)
    developer_apps_count = get_parameter_GET(
        request,
        'developerappscount',
        convert_func=int,
        required=False,
        default=8)
    review_count = get_parameter_GET(
        request,
        'reviewcount',
        convert_func=int,
        required=False,
        default=3)
    platform = get_parameter_GET(
        request,
        'platform',
        convert_func=int,
        default=1)
    jailbreak = get_parameter_GET(
        request,
        'jailbreak',
        convert_func=int,
        default=0) == 1
    for q in (client_id, source):
        if isinstance(q, HttpResponse):
            return q

    result = get_app(
        app_id,
        package_name,
        platform=platform,
        jailbreak=jailbreak)
    if not result:
        return {}

    # Fix platform based on the app info
    app_platform = result.get('platform', None)
    if app_platform and isinstance(app_platform, list):
        platform = app_platform[0]

    # platform = 1: enable for android only
    if platform == 1 and developer_apps_count and 'package_sig' in result:
        result['developer_apps'] = append_icon_host(
            app_db.get_info_for_same_developer_apps(result['package_sig'],
                                                    platform,
                                                    result.get('app_type',
                                                               None),
                                                    result['id'],
                                                    count=developer_apps_count))

    if review_count:
        result['reviews'] = QueryReviewAction(
            app_db,
            logger).query_reviews(result['id'],
                                  count=review_count)

    return app_post_process(result, related_apps_count=related_apps_count)

app_upload_logger = logging.getLogger('uploadapplist')


@require_POST
@json_response
def app_updates(request):
    '''
    clientid: client's unique id, client refers to the device where apps to be installed on
    source: where the app update request is sent from, usually consists of "<package_name>+<version_code>"
    deviceinfo: a piece of info which usually consists of "<model_name>+<os_version>"
    '''
    compact = get_parameter_GET(
        request,
        'compact',
        convert_func=int,
        required=False,
        default=None)
    if compact is not None:
        client_id = get_parameter_GET(request, 'clientid')
        source = get_parameter_GET(request, 'source')
        app_infos = []
        if compact == 1:
            for arg in request.raw_post_data.split('&'):
                kv = arg.split('=', 1)
                if len(kv) != 2:
                    continue
                if kv[0] == 'ks[]':
                    fields = kv[1].split('|')
                    if len(fields) != 2:
                        continue
                    app_infos.append({
                        "packageName": fields[0],
                        "packageVersion": long(fields[1]),
                        "packageSig": "",
                        "appName": "",
                    })
                elif kv[0] == 'os':
                    os = int(kv[1])
        elif compact == 2:
            http_head = get_parameter_META(
                request,
                'HTTP_HEAD',
                convert_func=simplejson.loads,
                required=False,
                default=u'')
            os = http_head['sdk']
            p = get_parameter_POST(request, 'p')
            p = simplejson.loads(p) if p else None
            if p:
                for k, v in p.iteritems():
                    app_infos.append({
                        "packageName": k,
                        "packageVersion": 0,
                        "packageSig": "",
                        "appName": v,
                    })
    else:
        client_id = get_parameter_POST(request, 'clientid')
        source = get_parameter_POST(request, 'source')
        app_infos = get_parameter_POST(
            request,
            'appinfos',
            convert_func=simplejson.loads)
        os = get_parameter_POST(
            request,
            'os',
            required=False,
            convert_func=int,
            default=None)
    device_info = get_parameter_POST(request, 'deviceinfo', required=False)
    screen_size = get_parameter_POST(request, 'screensize', required=False)
    platform = get_parameter_POST(
        request,
        'platform',
        convert_func=to_int_array,
        default='1')
    jailbreak = get_parameter_POST(
        request,
        'jailbreak',
        convert_func=int,
        default=0)
    save_to_db = get_parameter_GET(
        request,
        'savetodb',
        convert_func=int,
        default=1) == 1
    ip = get_parameter_META(
        request,
        'REMOTE_ADDR',
        required=False,
        default=u'')
    with_details = get_parameter_GET(
        request,
        'details',
        convert_func=bool,
        required=False)
    for q in (client_id, source, device_info, app_infos, ip):
        if isinstance(q, HttpResponse):
            logger.info(
                'app_updates, ip=%s, clientid=%s, invalid request' %
                (ip, client_id))
            return q

    if jailbreak == -1:
        # this is used for pc client, for which, there's no jailbreak concept,
        # and it requires the app to keep the jailbreak status
        jailbreak = None
    elif jailbreak == 1:
        jailbreak = True
    else:
        jailbreak = False

    if len(platform) == 1:
        platform = platform[0]

    log_data = '|'.join([str(app_info['packageName']) + ':' + str(app_info['packageVersion'])
                        for app_info in app_infos])
    app_upload_logger.info('ip=%s, clientid=%s, source=%s, deviceinfo=%s, appinfos=%s, os=%s, screensize=%s, platform=%s, jailbreak=%s, savetodb=%s, compact=%s'
                           % (ip, client_id, source, device_info, log_data, str(os), screen_size, str(platform), str(jailbreak), str(save_to_db), str(compact)))

    for app in app_infos:
        app['packageVersion'] = int(app['packageVersion'])

    if len(app_infos) > 0:
        user_app_data = {
            'apps': app_infos,
            'device_info': device_info,
            'os': os,
            'screen_size': screen_size,
            'platform': platform,
            'jailbreak': jailbreak,
            'source': source
        }
        if save_to_db:
            user_db.update_apps_installed(client_id, user_app_data)
    else:
        # client may update an empty list to just query the user app updates
        user_app_data = user_db.query_apps_installed(client_id)
        if user_app_data is not None and 'apps' in user_app_data:
            app_infos = user_app_data['apps']

    if app_infos is not None and len(app_infos) > 0:
        if jailbreak is not None:
            results = app_db.query_updates(
                app_infos,
                platform=platform,
                jailbreak=jailbreak)
        else:
            results = app_db.query_updates(
                [app for app in app_infos if app['appType'] == 0],
                platform=platform,
                jailbreak=jailbreak)
            results += app_db.query_updates(
                [app for app in app_infos if app['appType'] != 0],
                platform=platform, jailbreak=jailbreak)
    else:
        results = []

    # support incremental updates
    for r in results:
        r['patch_size'] = 0    # 0 by default
        app = [a for a in app_infos if a['packageName'] == r['package_name']]
        if app:
            app = app[0]
            old_hash, new_hash = app.get(
                'packageHash', None), r.get('package_hash', None)
            if old_hash and new_hash:
                old_hash = old_hash.lower()
                patch_info = patch_db.get_patch_info(old_hash, new_hash)
                if patch_info:
                    r['patch_size'] = friendly_size(patch_info['patch_size'])
                # else:
                    # On demand calculate patch
                    #patch_db.add_job(old_hash, new_hash)
                del r['package_hash']
        else:
            continue

    results = app_post_process(
        results,
        with_details=with_details,
        os=os,
        screen_size=screen_size)
    logger.info(
        'app_updates, clientid=%s, results=%d' %
        (client_id, len(results)))
    return results


@json_response
def app_reviews(request):
    if request.method == "GET":
        client_id = get_parameter_GET(request, 'clientid')
        app_id = get_parameter_GET(
            request,
            'app_id',
            convert_func=int,
            required=False)
        app_name = get_parameter_GET(request, 'appname', required=False)
        start_index = get_parameter_GET(
            request,
            'start_index',
            convert_func=int)
        count = get_parameter_GET(request, 'count', convert_func=int)
        with_total = get_parameter_GET(
            request,
            'wt',
            convert_func=bool,
            required=False)
        for q in (client_id, app_id, start_index, count):
            if isinstance(q, HttpResponse):    # convert failed
                return q
        if not app_id and not app_name:
            return (
                parameter_error(
                    request,
                    'either of [app_id, appname] is required')
            )

        if not app_id:
            app = app_db.get_app_by_name(app_name)
            if not app:
                return []
            app_id = app['id']

        results = app_db.query_reviews(
            app_id,
            start_index=start_index,
            count=count,
            with_total=with_total)
        logger.info('app_reviews, client_id=%s, results=%s'
                    % (client_id, _result_info(results)))

        return results
    elif request.method == "POST":
        client_id = get_parameter_POST(request, 'clientid')
        review = get_parameter_POST(
            request,
            'review',
            convert_func=simplejson.loads)
        ip = get_parameter_META(
            request,
            'REMOTE_ADDR',
            required=False,
            default=u'')
        for q in (client_id, review, ip):
            if isinstance(q, HttpResponse):    # convert failed
                return q
        review['client_id'] = client_id
        app_db.save_reviews([review])

        logger.info('app_reviews, post, client_id=%s, ip=%s, review_id=%d'
                    % (client_id, ip, review['id']))


def app_download_internal_by_download_url(
        download_path, package_name, version_code, is_rename=True, old_hash=None):
    if is_rename and download_path.find('?') == -1:
        # Convert download path into user and CDN friendly path. For example,
        #     downloads/vol1/attachments/2010/05/4005_127358798077.apk
        # will be converted to:
        # downloads/vol1/<package_name>_<version_code>.apk?p=attachments/2010/05/4005_127358798077.apk
        ext = os.path.splitext(download_path)[1]
        if ext == ".patch":
            version_str = "%s_%s" % (version_code, old_hash)
        else:
            version_str = "%s" % version_code

        download_path = "%s%s_%s%s?p=%s" % (download_path[:download_path.find("/", len("downloads/")) + 1],
                                            package_name,
                                            version_str,
                                            ext,    # file suffix
                                            download_path[download_path.find("/", len("downloads/") + 1) + 1:])

    url = build_apk_url(download_path)
    return HttpResponseRedirect(url)

# RETURN (download_app, use_download_app, download_from)


def process_app_download(client_id, source, store_app,
                         external_url):
    # try store app
    if store_app:
        return (store_app, True, 'store')

    # try external
    if external_url:
        return (store_app, False, 'externalurl')

    return None


@require_GET
def app_download(request, app_id=None, source=None):
    client_id = get_parameter_GET(
        request,
        'clientid',
        required=False,
        default='')
    if not source:
        source = get_parameter_GET(
            request,
            'source',
            required=False,
            default='')
    if not app_id:
        app_id = get_parameter_GET(
            request,
            'app_id',
            convert_func=int,
            required=False,
            default=None)
    package_name = get_parameter_GET(
        request,
        'packagename',
        required=False,
        default=None)
    is_rename = get_parameter_GET(
        request,
        'rn',
        convert_func=bool,
        required=False,
        default=True)
    version_code = get_parameter_GET(
        request,
        'versioncode',
        convert_func=int,
        required=False)
    external_url = get_parameter_GET(request, 'externalurl', required=False)
    platform = get_parameter_GET(
        request,
        'platform',
        convert_func=int,
        default=1)
    jailbreak = get_parameter_GET(
        request,
        'jailbreak',
        convert_func=int,
        default=0) == 1
    old_hash = get_parameter_GET(
        request,
        'old_hash',
        required=False,
        default=None)
    ip = get_parameter_META(
        request,
        'REMOTE_ADDR',
        required=False,
        default=u'')

    for q in (client_id, app_id, package_name):
        if isinstance(q, HttpResponse):
            return q
    if not app_id and not package_name:
        return (
            parameter_error(
                request,
                'either of [app_id, packagename] is required')
        )

    store_app = get_app(
        app_id=app_id,
        package_name=package_name,
        platform=platform,
        jailbreak=jailbreak)
    if store_app:
        app_id = store_app['id']
        package_name = store_app['package_name']

    # get download info
    download_info = process_app_download(
        client_id,
        source,
        store_app,
        external_url)

    download_from = 'NA'
    download_app = None
    use_download_app = None
    if download_info:
        (download_app, use_download_app, download_from) = download_info

    # log
    logger.info('app_download, clientid=%s, source=%s, ip=%s, package=%s, version=%s, externalurl=%s, id=%s, downversion=%s, downurl=%s, downfrom=%s'
                % (client_id, source, ip, str(package_name), str(version_code), str(external_url), str(app_id), str(download_app['version_code']) if download_app else 'NA', download_app['download_url'] if download_app else 'NA', download_from))

    # redirect to download
    if use_download_app:
        is_rename = True
        new_hash = download_app.get('package_hash')
        download_url = None
        if old_hash and new_hash:
            old_hash = old_hash.lower()
            download_url = patch_db.get_patch_url(old_hash, new_hash)
            # if not download_url:
                # On demand calculate patch
                #patch_db.add_job(old_hash, new_hash)
        if not download_url:
            download_url = download_app['download_url']
        return (
            app_download_internal_by_download_url(
                download_url,
                download_app['package_name'],
                download_app['version_code'],
                is_rename=is_rename)
        )
    if external_url:
        return HttpResponseRedirect(external_url)
    return resource_not_exist(request, app_id if app_id else package_name)


@require_GET
def share_app_download(request, app_id):
    return app_download(request, app_id=app_id, source='share')


def request_handler(request, client_id, source, path):
    request.encoding = 'gbk'
    # TODO: validate source
    ip = get_parameter_META(
        request,
        'REMOTE_ADDR',
        required=False,
        default=u'')
    url = path

    if len(request.GET) > 0:
        data = urllib.urlencode(dict([k, unicode(v).encode('gbk')]
                                for k, v in request.GET.items()))
        url = url + '?' + data
    postdata = simplejson.dumps(request.POST)
    ks = request.GET.getlist('ks[]')
    if ks:
        postdata += ", ks=" + simplejson.dumps(ks)

    # redirect requests, set False if we have handled all the requests
    redirect_request = True
    warning_tag = ''
    if not url.startswith('openbox.mobilem.360.cn/AppStore/getSuggest'):
        warning_tag = ', WARNING:UNKNOWNREQUEST'
        redirect_request = True

    logger.info('request_handler, clientid=%s, source=%s, ip=%s, path=%s, method=%s, postdata=%s, rawpostdata=%s, unhandled%s'
                % (client_id, source, ip, url, request.method, postdata, request.raw_post_data, warning_tag))

    if request.method == 'GET' and redirect_request:
        return HttpResponseRedirect('http://' + url)
    return HttpResponse('ok', status=200)


@require_GET
def app_blacklist(request):
    client_id = get_parameter_GET(request, 'clientid')
    source = get_parameter_GET(request, 'source')
    ip = get_parameter_META(
        request,
        'REMOTE_ADDR',
        required=False,
        default=u'')
    start_index = get_parameter_GET(
        request,
        'start_index',
        convert_func=int,
        required=False,
        default=u'0')
    count = get_parameter_GET(
        request,
        'count',
        convert_func=int,
        required=False,
        default=u'0')
    if_modified_since = get_parameter_META(
        request,
        'HTTP_IF_MODIFIED_SINCE',
        convert_func=parser.parse,
        required=False,
        default=None)
    for q in (client_id, source, ip, start_index, count):
        if isinstance(q, HttpResponse):    # convert failed
            return q

    updatetime = app_db.query_blacklist_update_time()
    logger.info('app_blacklist, clientid=%s, source=%s, ip=%s, ims=%s, ut=%s'
                % (client_id, source, ip, if_modified_since, updatetime))
    if updatetime is None or (if_modified_since is not None and updatetime <= if_modified_since):
        return HttpResponseNotModified()

    data = app_db.query_blacklist(start_index, count)
    response = HttpResponse(
        simplejson.dumps(data),
        content_type='application/json; charset=utf-8')
    response['Last-Modified'] = updatetime
    return response


@require_POST
@json_response
def client_activate(request):
    client_id = get_parameter_POST(request, 'clientid')
    source = get_parameter_POST(request, 'source')
    ip = get_parameter_META(
        request,
        'REMOTE_ADDR',
        required=False,
        default=u'')
    data = get_parameter_POST(request, 'data')
    for q in (client_id, source, data):
        if isinstance(q, HttpResponse):    # convert failed
            return q

    logger.info('client_activate, clientid=%s, source=%s, ip=%s, data=%s'
                % (client_id, source, ip, data))
    return {'ok': 1}


@require_GET
@json_response
def app_related_apps(request):
    client_id = get_parameter_GET(request, 'clientid')
    source = get_parameter_GET(request, 'source')
    app_id = get_parameter_GET(
        request,
        'app_id',
        convert_func=int,
        required=False)
    package_name = get_parameter_GET(request, 'packagename', required=False)
    start_index = get_parameter_GET(
        request,
        'start_index',
        convert_func=int,
        required=False,
        default=0)
    count = get_parameter_GET(
        request,
        'count',
        convert_func=int,
        required=False,
        default=10)
    os = get_parameter_GET(
        request,
        'os',
        required=False,
        convert_func=int,
        default=None)
    screen_size = get_parameter_GET(request, 'screensize', required=False)
    with_details = get_parameter_GET(
        request,
        'details',
        convert_func=bool,
        required=False)
    platform = get_parameter_GET(
        request,
        'platform',
        convert_func=int,
        default=1)
    jailbreak = get_parameter_GET(
        request,
        'jailbreak',
        convert_func=int,
        default=0) == 1
    for q in (client_id, source, start_index, count):
        if isinstance(q, HttpResponse):
            return q
    if not app_id and not package_name:
        return (
            parameter_error(
                request,
                'either of [app_id, packagename] is required')
        )

    if not app_id:
        app = get_app(
            app_id,
            package_name,
            platform=platform,
            jailbreak=jailbreak)
        if not app:
            return []
        app_id = app['id']

    related_app_list = app_db.get_related_apps(app_id)

    if related_app_list and 'related_apps' in related_app_list:
        related_app_list = related_app_list['related_apps']

    if not related_app_list:
        return []

    return (
        app_post_process(
            related_app_list,
            with_details=with_details,
            os=os,
            screen_size=screen_size)
    )


@require_GET
@json_response
def app_developer_apps(request):
    client_id = get_parameter_GET(request, 'clientid')
    source = get_parameter_GET(request, 'source')
    app_id = get_parameter_GET(request, 'app_id', required=False)
    package_name = get_parameter_GET(request, 'packagename', required=False)
    start_index = get_parameter_GET(
        request,
        'start_index',
        convert_func=int,
        required=False,
        default=0)
    count = get_parameter_GET(
        request,
        'count',
        convert_func=int,
        required=False,
        default=0)
    os = get_parameter_GET(
        request,
        'os',
        required=False,
        convert_func=int,
        default=None)
    screen_size = get_parameter_GET(request, 'screensize', required=False)
    with_details = get_parameter_GET(
        request,
        'details',
        convert_func=bool,
        required=False)
    platform = get_parameter_GET(
        request,
        'platform',
        convert_func=int,
        default=1)
    jailbreak = get_parameter_GET(
        request,
        'jailbreak',
        convert_func=int,
        default=0) == 1
    for q in (client_id, source, start_index, count):
        if isinstance(q, HttpResponse):
            return q
    if not app_id and not package_name:
        return (
            parameter_error(
                request,
                'either of [app_id, packagename] is required')
        )

    app = get_app(app_id, package_name, platform=platform, jailbreak=jailbreak)
    if not app or 'package_sig' not in app:
        return []

    developer_apps = app_db.get_info_for_same_developer_apps(
        app['package_sig'],
        platform)
    if not developer_apps:
        return []
    return (
        app_post_process(
            developer_apps,
            with_details=with_details,
            os=os,
            screen_size=screen_size)
    )
