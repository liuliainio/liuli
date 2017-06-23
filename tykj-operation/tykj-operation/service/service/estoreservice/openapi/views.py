# -*- coding: utf-8 -*-
import os
import re
import logging
from dateutil import parser
from django.conf import settings
from django.utils import simplejson
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotModified
from django.views.decorators.http import require_GET, require_POST
from estorecore.db import timestamp_utc_now,MongodbStorage
from estorecore.servemodels.app import AppMongodbStorage, APPLIST_ITEM_TYPE_APPDETAIL, APP_FIELDS_LIST_DETAILS_WITH_PROMOTE
from estorecore.servemodels.user import UserMongodbStorage
from estorecore.servemodels.patch import PatchMongodbStorage
from estorecore.utils import friendly_size
from estoreservice.utils.utils import json_response, append_icon_host, build_img_url, \
    to_int_array, build_apk_url, combine_url
from estoreservice.openapi.errors import parameter_error, resource_not_exist, authentication_fail
from estoreservice.openapi.utils import get_parameter_GET, get_parameter_POST, get_parameter_META

from estoreservice.utils.parameterparser import parse_parameters
from estoreservice.utils.requestparameters import *
from estoreservice.api.actions.appupdateaction import AppUpdateAction
from estoreservice.api.actions.reviewactions import PostReviewAction, QueryReviewAction
from estoreservice.api.actions.downloadaction import DownloadAction


logger = logging.getLogger('estoreservice.openapi')
app_db = AppMongodbStorage(settings.MONGODB_CONF)
user_db = UserMongodbStorage(settings.MONGODB_CONF)
patch_db = PatchMongodbStorage(settings.MONGODB_CONF)

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
_convert_category_apps_order = partial(
    _convert_order,
    order_dicts=CATEGORY_APPS_ORDERS)


def _check_apikey(func):
    """
        for legency issues, client will use ChannelName(chn) as apikey
    """

    def _view(request, *args, **kwargs):
        chn = request.GET.get('chn', None) or request.POST.get('chn', None)
        if not chn or not user_db.is_enable_apikey(chn):
            return authentication_fail(request)
        return func(request, *args, **kwargs)

    return _view


def _try_query(func, apikey, list_id=None, *args, **kwargs):
    """
        for all app list like api, we will try "apikey-id" as list id, if failed,
        we will try to get list with id passed

        for apikey base query, we will try 'apikey' query, if failed,
        we will try to get with apikey=None,
    """

    if list_id:
        try_list_id = '%s-%s' % (apikey, list_id)
        results = func(*args, app_list_id=try_list_id, **kwargs)
        if not results:
            results = func(*args, app_list_id=list_id, **kwargs)
    else:
        results = func(*args, apikey=apikey, **kwargs)
        if not results:
            results = func(*args, apikey=None, **kwargs)
    return results


def _result_info(results, formatter=lambda x: x['id'] if 'id' in x else ''):
    if isinstance(results, dict):
        if 'results' in results and results['results']:
            return [formatter(r) for r in results['results']]
        if 'id' in results:
            results = formatter(results)
    if isinstance(results, list):
        if results and 'id' in results[0]:
            return [formatter(r) for r in results]
    return results


def _gen_small_preview_icon_url(url):
    if not url:
        return url
    if not url.startswith('img'):
        return url
    return 's_' + url


def _is_app_supported(app, os, screen_size):
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
                      related_apps_count=0, os=None, screen_size=None, chn=None):
    is_list = True
    if not isinstance(apps, list):
        apps = [apps]
        is_list = False

    if is_list:
        # it's ok to set os=None and screen_size=None, if you put the filter
        # logic in the db selection
        if os or screen_size:
            apps = [
                app for app in apps if _is_app_supported(
                    app,
                    os,
                    screen_size)]

    if with_details:
        apps = app_db.get_apps_with_details(
            apps,
            fields=APP_FIELDS_LIST_DETAILS_WITH_PROMOTE)

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
                    _gen_small_preview_icon_url(img)) for img in re.split(',| ',
                                                                          app['preview_icon_urls'])])
            app['preview_icon_urls'] = ','.join(
                [build_img_url(img) for img in re.split(',| ', app['preview_icon_urls'])])
        if 'apps' in app:    # for subject items
            app['apps'] = append_icon_host(app['apps'])
        if 'promote' in app:
            del app['promote']

        if 'promote_apps' in app and chn in app['promote_apps']:
            promote_app = app['promote_apps'][chn]
            for k, v in APP_FIELDS_LIST_DETAILS_WITH_PROMOTE.iteritems():
                if v == 1 and k in promote_app:
                    app[k] = promote_app[k]

        if 'promote_apps' in app:
            del app['promote_apps']

    append_icon_host(apps)

    return apps if is_list else apps[0]


def app_post_process(apps, with_details=False,
                     related_apps_count=0, os=None, screen_size=None, chn=None):
    if not apps:
        return apps
    if isinstance(apps, dict) and 'results' in apps:
        apps['results'] = _app_post_process(
            apps['results'],
            with_details,
            related_apps_count,
            os,
            screen_size,
            chn=chn)
    else:
        apps = _app_post_process(
            apps,
            with_details,
            related_apps_count,
            os,
            screen_size,
            chn=chn)
    return apps


def get_app(app_id, package_name, platform=1, jailbreak=False):
    app = None
    if app_id:
        app = app_db.get_info(
            int(app_id),
            fields=APP_FIELDS_LIST_DETAILS_WITH_PROMOTE)
    elif package_name:
        app = app_db.get_app_by_package(
            package_name,
            platform=platform,
            jailbreak=jailbreak,
            fields=APP_FIELDS_LIST_DETAILS_WITH_PROMOTE)
    return app


@_check_apikey
@require_GET
@json_response
def app_categories(request):
    client_id = get_parameter_GET(request, 'clientid')
    chn = get_parameter_GET(request, 'chn')
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
    for q in (chn, client_id, parent_categories, start_index, count):
        if isinstance(q, HttpResponse):    # convert failed
            return q

    results = append_icon_host(
        app_db.query_categories(
            parent_categories=parent_categories,
            start_index=start_index,
            count=count,
            with_total=with_total))
    logger.info(
        'app_categories, chn=%s, clientid=%s, results=%s',
        chn,
        client_id,
        str(results))
    return results


def find_black_words(s, words):
    if isinstance(s, str):
        s = s.decode('utf8')
    s = s.lower()
    for word in words:
        if s.find(word) != -1:
            return word
    return None


@_check_apikey
@require_GET
@json_response
def app_category_apps(request):
    client_id = get_parameter_GET(request, 'clientid')
    chn = get_parameter_GET(request, 'chn')
    cate_id = get_parameter_GET(request, 'cate_id', convert_func=to_int_array)
    cate_level = get_parameter_GET(
        request,
        'catelevel',
        convert_func=int,
        default=1)    # 0: top category, 1: sub category
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
    update_date_from = get_parameter_GET(
        request,
        'update_date_from',
        convert_func=int,
        required=False,
        default=0)
    update_date_to = get_parameter_GET(
        request,
        'update_date_to',
        convert_func=int,
        required=False,
        default=0)
    debug = 0

    for q in (chn, client_id, cate_id, order, start_index, count):
        if isinstance(q, HttpResponse):    # convert failed
            return q

    if len(cate_id) == 1 and cate_id[0] == 0:
        # set default cate ids
        cate_id = [14334, 14357]

    app_list = None
    extra_fields = None
    results = app_db.query_category_apps(
        category_id=cate_id, cate_level=cate_level, platform=platform,
        app_type=app_type, start_index=start_index, count=count, order=order, with_total=with_total,
        update_date_from=update_date_from, update_date_to=update_date_to, extra_fields=extra_fields, app_list=app_list)

    logger.info(
        'app_category_apps, chn=%s, clientid=%s, results=%s',
        chn,
        client_id,
        str(_result_info(results)))

    results = app_post_process(
        results,
        with_details=with_details,
        related_apps_count=related_apps_count,
        chn=chn)

    if debug:
        results = {'results': results, 'blocked_apps': blocked_apps}

    return results


@_check_apikey
@require_GET
@json_response
def app_list_apps(request):
    client_id = get_parameter_GET(request, 'clientid')
    chn = get_parameter_GET(request, 'chn')
    source = get_parameter_GET(request, 'source')
    app_list_id = get_parameter_GET(request, 'list_id')
    os_v = get_parameter_GET(
        request,
        'os',
        required=False,
        convert_func=int,
        default=None)
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
    with_short_desc = get_parameter_GET(
        request,
        'shortdesc',
        convert_func=int,
        required=False)
    related_apps_count = get_parameter_GET(
        request,
        'relatedappscount',
        convert_func=int,
        required=False)
    for q in (chn, client_id, source, app_list_id, start_index, count):
        if isinstance(q, HttpResponse):    # convert failed
            return q

    extra_fields = None
    if with_short_desc:
        extra_fields = {'description': 1}

    results = _try_query(
        app_db.query_apps_from_list,
        chn,
        list_id=app_list_id,
        start_index=start_index,
        count=count,
        with_total=with_total,
        extra_fields=extra_fields)

    if with_short_desc:
        for result in results:
            if not result.get('short_description', None):
                result['short_description'] = result.get(
                    'description',
                    '')[0: 50]
            if 'description' in result:
                del result['description']

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
        'app_list_apps, chn=%s, clientid=%s, results=%s',
        chn,
        client_id,
        str(_result_info(results)))

    return (
        app_post_process(
            results,
            os=os_v,
            with_details=with_details,
            related_apps_count=related_apps_count,
            chn=chn)
    )


@_check_apikey
@require_GET
@json_response
def app_subjects(request):
    client_id = get_parameter_GET(request, 'clientid')
    chn = get_parameter_GET(request, 'chn')
    app_list_id = get_parameter_GET(request, 'app_list_id')
    start_index = get_parameter_GET(request, 'start_index', convert_func=int)
    count = get_parameter_GET(request, 'count', convert_func=int)
    with_total = get_parameter_GET(
        request,
        'wt',
        convert_func=bool,
        required=False)
    for q in (chn, client_id, app_list_id, start_index, count):
        if isinstance(q, HttpResponse):    # convert failed
            return q

    results = _try_query(
        app_db.query_subjects,
        chn,
        list_id=app_list_id,
        start_index=start_index,
        count=count,
        with_total=with_total)
    logger.info(
        'app_subjects, chn=%s, clientid=%s, results=%s',
        chn,
        client_id,
        str(_result_info(results)))

    return append_icon_host(results)


@_check_apikey
@require_GET
@json_response
def app_subject_apps(request):
    client_id = get_parameter_GET(request, 'clientid')
    chn = get_parameter_GET(request, 'chn')
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
    for q in (chn, client_id, subject_id, start_index, count):
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
    logger.info(
        'app_subject_apps, chn=%s, clientid=%s, results=%s',
        chn,
        client_id,
        str(_result_info(results)))

    return (
        app_post_process(
            results,
            with_details=with_details,
            related_apps_count=related_apps_count,
            chn=chn)
    )


@_check_apikey
@require_GET
@json_response
def app_info(request):
    client_id = get_parameter_GET(request, 'clientid')
    chn = get_parameter_GET(request, 'chn')
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
    for q in (chn, client_id):
        if isinstance(q, HttpResponse):
            return q

    result = get_app(
        app_id,
        package_name,
        platform=platform,
        jailbreak=jailbreak)
    if not result:
        return {}

    if developer_apps_count and 'package_sig' in result:
        result['developer_apps'] = append_icon_host(
            app_db.get_info_for_same_developer_apps(result['package_sig'],
                                                    result['id'],
                                                    count=developer_apps_count))

    if review_count:
        result['reviews'] = QueryReviewAction(
            app_db,
            logger).query_reviews(result['id'],
                                  count=review_count)

    if not 'screensize' in result:
        result['screensize'] = ''

    if result.get('package_name', '').startswith('com.diandian.appstore.producer.'):
        result['package_name'] = 'com.dolphin.browser.xf'

    results = app_post_process(
        result,
        related_apps_count=related_apps_count,
        chn=chn)
    logger.info(
        'app_info, chn=%s, clientid=%s, results=%s',
        chn,
        client_id,
        str(_result_info(results)))
    return results


app_upload_logger = logging.getLogger('uploadapplist')


@_check_apikey
@require_POST
@json_response
def app_updates(request):
    '''
    clientid: client's unique id, client refers to the device where apps to be installed on
    source: where the app update request is sent from, usually consists of "<package_name>+<version_code>"
    deviceinfo: a piece of info which usually consists of "<model_name>+<os_version>"
    '''
    client_id = get_parameter_POST(request, 'clientid')
    chn = get_parameter_GET(
        request,
        'chn',
        required=False,
        default=None) or get_parameter_POST(
        request,
        'chn')
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
    ip = get_parameter_META(
        request,
        'REMOTE_ADDR',
        required=False,
        default=u'')
    for q in (chn, client_id, source, device_info, app_infos, ip):
        if isinstance(q, HttpResponse):
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
    app_upload_logger.info('chn=%s, ip=%s, clientid=%s, source=%s, deviceinfo=%s, appinfos=%s, os=%s, screensize=%s, platform=%s, jailbreak=%s'
                           % (chn, ip, client_id, source, device_info, log_data, str(os), screen_size, str(platform), str(jailbreak)))

    for app in app_infos:
        app['packageVersion'] = int(app['packageVersion'])
    if chn != 'ofw':
        app_infos = [app for app in app_infos if app['packageName']
                     != 'com.diandian.appstore']

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

    # only return chars max size 400  for update_note to save traffic.
    for r in results:
        if 'update_note' in r:
            r['update_note'] = r['update_note'][:400]

    results = app_post_process(
        results,
        os=os,
        screen_size=screen_size,
        chn=chn)
    logger.info(
        'app_updates, chn=%s, clientid=%s, results=%d' %
        (chn, client_id, len(results)))
    return results


@_check_apikey
@require_POST
@json_response
def app_updates2(request):
    action = AppUpdateAction(
        app_db=app_db,
        user_db=user_db,
        patch_db=patch_db,
        logger=logger,
        app_upload_logger=app_upload_logger)
    return action.execute(request)


@_check_apikey
@json_response
def app_reviews(request):
    pass


@_check_apikey
@require_GET
@parse_parameters(required_parameters=[(P_PACKAGE_NAME, P_APP_ID)], optional_parameters=[P_IS_RENAME, P_VERSION_CODE, P_PLATFORM, P_JAILBREAK, P_OLD_HASH])
def app_download(request, parameters):
    return (
        DownloadAction(
            app_db,
            patch_db,
            logger).process_download(
            request,
            parameters)
    )


@_check_apikey
@require_GET
@parse_parameters(required_parameters=[P_DOWNLOAD_URL, P_PAGE_URL], optional_parameters=[P_DISABLE_ME])
def app_download_from_dolphin(request, parameters):
    return (
        DownloadAction(
            app_db,
            patch_db,
            logger).process_dolphin_download(
            request,
            parameters)
    )


@_check_apikey
@require_POST
@json_response
def client_activate(request):
    client_id = get_parameter_POST(request, 'clientid')
    chn = get_parameter_GET(
        request,
        'chn',
        required=False,
        default=None) or get_parameter_POST(
        request,
        'chn')
    source = get_parameter_POST(request, 'source')
    ip = get_parameter_META(
        request,
        'REMOTE_ADDR',
        required=False,
        default=u'')
    data = get_parameter_POST(request, 'data')
    for q in (chn, client_id, source, data):
        if isinstance(q, HttpResponse):    # convert failed
            return q

    logger.info('client_activate, chn=%s, clientid=%s, source=%s, ip=%s, data=%s'
                % (chn, client_id, source, ip, data))
    return {'ok': 1}


@_check_apikey
@require_GET
@json_response
def app_related_apps(request):
    client_id = get_parameter_GET(request, 'clientid')
    chn = get_parameter_GET(request, 'chn')
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
    for q in (chn, client_id, source, start_index, count):
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

    logger.info('app_related_apps, chn=%s, clientid=%s, source=%s, package=%s, os=%s, id=%s, screen_size=%s, count=%d'
                % (chn, client_id, source, str(package_name), os, str(app_id), str(screen_size) if screen_size else 'NA', count))

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
            screen_size=screen_size,
            chn=chn)
    )


@_check_apikey
@require_GET
@json_response
def app_developer_apps(request):
    client_id = get_parameter_GET(request, 'clientid')
    chn = get_parameter_GET(request, 'chn')
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
    for q in (chn, client_id, source, start_index, count):
        if isinstance(q, HttpResponse):
            return q
    if not app_id and not package_name:
        return (
            parameter_error(
                request,
                'either of [app_id, packagename] is required')
        )

    logger.info('app_developer_apps, chn=%s, clientid=%s, source=%s, package=%s, os=%s, id=%s, screen_size=%s, count=%d'
                % (chn, client_id, source, str(package_name), os, str(app_id), str(screen_size) if screen_size else 'NA', count))

    app = get_app(app_id, package_name, platform=platform, jailbreak=jailbreak)
    if not app or 'package_sig' not in app:
        return []

    developer_apps = app_db.get_info_for_same_developer_apps(
        app['package_sig'],
        0)
    if not developer_apps:
        return []
    return (
        app_post_process(
            developer_apps,
            with_details=with_details,
            os=os,
            screen_size=screen_size,
            chn=chn)
    )


from estorecore.servemodels.promotion import PromotionMongodbStorage
promotion_db = PromotionMongodbStorage(settings.MONGODB_CONF)


@_check_apikey
@require_GET
@json_response
def login_pictures(request):
    client_id = get_parameter_GET(request, 'clientid')
    chn = get_parameter_GET(request, 'chn')
    for q in (chn, client_id):
        if isinstance(q, HttpResponse):    # convert failed
            return q
    results = _try_query(promotion_db.query_login_pictures, apikey=chn)
    results = append_icon_host(results)
    logger.info(
        'login_pictures, chn=%s, client_id=%s, results=%s' %
        (chn, client_id, results))
    return results


@_check_apikey
@require_GET
@json_response
def activities(request):
    chn = get_parameter_GET(request, 'chn')
    client_id = get_parameter_GET(request, 'clientid')
    belong_to = get_parameter_GET(request, 'belong_to')
    start_index = get_parameter_GET(request, 'start_index', convert_func=int)
    count = get_parameter_GET(request, 'count', convert_func=int)
    for q in (chn, client_id, belong_to, start_index, count):
        if isinstance(q, HttpResponse):    # convert failed
            return q

    results = promotion_db.query_activities(
        belong_to,
        start_index=start_index,
        count=count)
    logger.info('activities, chn=%s, client_id=%s, results=%s'
                % (chn, client_id, str([result['id'] for result in results])))

    return append_icon_host(results)


@_check_apikey
@json_response
def feedbacks(request):
    chn = get_parameter_GET(
        request,
        'chn',
        required=False,
        default=None) or get_parameter_POST(
        request,
        'chn')
    if get_parameter_GET(request, 'keepraw', required=False, default=u''):
        client_id = get_parameter_GET(request, 'clientid')
        source = get_parameter_GET(
            request,
            'source',
            required=False,
            default=u'')
        feedback = {
            'content': simplejson.dumps(request.GET),
            'keepraw': 1
        }
    else:
        client_id = get_parameter_POST(request, 'clientid')
        source = get_parameter_POST(
            request,
            'source',
            required=False,
            default=u'')
        feedback = get_parameter_POST(
            request,
            'feedback',
            convert_func=simplejson.loads)
    ip = get_parameter_META(
        request,
        'REMOTE_ADDR',
        required=False,
        default=u'')
    for q in (chn, client_id, feedback, ip):
        if isinstance(q, HttpResponse):    # convert failed
            return q

    feedback['client_id'] = client_id
    feedback['source'] = source
    promotion_db.save_feedbacks([feedback])
    logger.info('feedbacks, chn=%s, client_id=%s, ip=%s, feedback=%d'
                % (chn, client_id, ip, feedback['id']))

    return {'ok': True}

from estoreservice.api.views.push import process_push_request


#@_check_apikey
#@require_POST
@json_response
def push_notification_messages(request):
    return process_push_request(request, logger, from_openapi=True)


from estorecore.servemodels.search import SearchMongodbStorage
search_db = SearchMongodbStorage(settings.MONGODB_CONF)
max_search_hot_keywords = 100


@_check_apikey
@require_GET
@json_response
def search_hot_keywords(request):
    client_id = get_parameter_GET(request, 'clientid')
    chn = get_parameter_GET(request, 'chn')
    start_index = get_parameter_GET(request, 'start_index', convert_func=int)
    count = get_parameter_GET(request, 'count', convert_func=int)
    for q in (chn, client_id, start_index, count):
        if isinstance(q, HttpResponse):
            return q

    if count <= 0:
        return []

    count = min(max_search_hot_keywords, count)
    results = _try_query(
        search_db.query_hot_keywords,
        apikey=chn,
        start_index=start_index,
        count=count)
    logger.info(
        'search_hot_keywords, chn=%s, client_id=%s, results=%s' %
        (chn, client_id, str([result['keyword'] for result in results])))

    return results

from estorecore.servemodels.update import UpdateMongodbStorage
update_db = UpdateMongodbStorage(settings.MONGODB_CONF)


@_check_apikey
@require_GET
@json_response
def update_service(request):
    client_id = get_parameter_GET(request, 'clientid')
    chn = get_parameter_GET(request, 'chn')
    pn = get_parameter_GET(request, 'pn')
    src = get_parameter_GET(request, 'src')
    vn = get_parameter_GET(request, 'vn', convert_func=int)
    auto = get_parameter_GET(request, 'auto', required=False)
    did = get_parameter_GET(request, 'did', required=False)
    os = get_parameter_GET(request, 'os', required=False)
    osvn = get_parameter_GET(request, 'osvn', required=False)
    re = get_parameter_GET(request, 're', required=False)
    # does not process currently
    cpu = get_parameter_GET(request, 'cpu', required=False)
    md = get_parameter_GET(request, 'md', required=False)
    rom = get_parameter_GET(request, 'rom', required=False)
    old_hash = get_parameter_GET(request, 'old_hash', required=False)
    #partner = get_parameter_GET(request, 'partner', required=False, default=u'xianxia')
    #broker = get_parameter_GET(request, 'broker', required=False, default=u'')

    for q in (chn, pn, src, vn):
        if isinstance(q, HttpResponse):    # convert failed
            return q
    result = update_db.get_update(
        pn, src, vn, is_auto=auto, device_id=did, os=os,
        os_version=osvn, resolution=re, cpu=cpu, device_model=md, rom=rom, client_id=client_id, chn=chn, old_hash=old_hash)
    if result is not None:
        if 'download_link' in result:
            result['download_url'] = result['download_link']
        if 'download_url' in result:
            result['download_url'] = combine_url(
                settings.APK_HOST,
                result['download_url'])

    logger.info('update_service, chn=%s, client_id=%s, rvc=%s, rurl=%s' % (
        chn,
        client_id,
        str(result.get('version_code', '')),
        result.get('download_url', ''))
    )
    return result


@_check_apikey
@require_GET
@json_response
def app_blacklist(request):
    client_id = get_parameter_GET(request, 'clientid')
    chn = get_parameter_GET(request, 'chn')
    source = get_parameter_GET(request, 'source')
    ip = get_parameter_META(
        request,
        'REMOTE_ADDR',
        required=False,
        default=u'')
    start_index = get_parameter_GET(request, 'start_index', convert_func=int)
    count = get_parameter_GET(request, 'count', convert_func=int)
    if_modified_since = get_parameter_META(
        request,
        'HTTP_IF_MODIFIED_SINCE',
        convert_func=parser.parse,
        required=False,
        default=None)
    for q in (client_id, chn, source, ip, start_index, count):
        if isinstance(q, HttpResponse):    # convert failed
            return q

    updatetime = app_db.query_blacklist_update_time()
    logger.info('app_blacklist, clientid=%s, chn=%s, source=%s, ip=%s, ims=%s, ut=%s'
                % (client_id, chn, source, ip, if_modified_since, updatetime))
    if updatetime is None or (if_modified_since is not None and updatetime <= if_modified_since):
        return HttpResponseNotModified()

    data = app_db.query_blacklist(start_index, count, apikey=chn)
    response = HttpResponse(
        simplejson.dumps(data),
        content_type='application/json; charset=utf-8')
    response['Last-Modified'] = updatetime
    return response


import random
import os as OS
from estorecore.servemodels.upload import UploadMongodbStorage
from estoreservice.decorators import exception_handled
from estoreservice.utils.utils import json_response_ok, json_response_error
from estoreservice.utils.resp_code import PARAM_REQUIRED, SAVE_FILE_ERROR
from estoreservice.utils import date_today, unix_time
from estoreservice.settings import UPLOAD_ROOT, UPLOAD_FILE_TYPE


upload_db = UploadMongodbStorage(settings.MONGODB_CONF)


def generate_file_path(package):
    udir = OS.path.join(UPLOAD_ROOT, package, date_today(package))
    if not OS.path.exists(udir):
        OS.makedirs(udir)
    while True:
        name = '%s%s' % (str(unix_time())[2:],
                         str(random.randint(10000, 99999)))
        fpath = '%s.%s' % (name, UPLOAD_FILE_TYPE)
        if not OS.path.exists(fpath):
            break
    return OS.path.join(udir, fpath)


@_check_apikey
@exception_handled
def crash_report(request):
    '''
    Update the report file
    Multipart POST parameters:
        package: package name and version

    Return:
    {
        "status": 0,
        "data": {
        }
    }
    '''
    post = request.POST
    package = post.get('package')

    if not package or 'report' not in request.FILES:
        return json_response_error(PARAM_REQUIRED, 'Parameters is not valid')

    snippet_file = request.FILES['report']

    # use +8 timezone for all counts
    upload_db.count_crash(date_today(''))

    try:
        fpath = generate_file_path(package)
    except Exception as e:
        logger.error('SAVE_FILE_ERROR - Check dir failed with exception %s', e)
        return json_response_error(SAVE_FILE_ERROR, 'Save failed')

    audio_file = open(fpath, 'wb')
    try:
        for chunk in snippet_file.chunks():
            audio_file.write(chunk)
    except Exception as e:
        logger.error(
            'SAVE_FILE_ERROR - Write report file failed with exception %s',
            e)
        return json_response_error(SAVE_FILE_ERROR, 'Save failed')
    finally:
        audio_file.close()

    return json_response_ok()


@_check_apikey
@require_GET
@json_response
def get_app_reviews(request):
    action = QueryReviewAction(app_db, logger)
    return action.execute(request)


@_check_apikey
@require_POST
@json_response
def post_app_review(request):
    action = PostReviewAction(app_db, logger)
    return action.execute(request)


from estoreservice.openapi.statistics import StatistcMongoDB
from estorecore.db import timestamp_utc_now
from estoreservice.utils.utils import json_response_error, json_response_ok
# @_check_apikey
@require_GET
@json_response
def client_statistics(request):
    _ERR_CODE_ILL_PARAM = "Illegal Parameter"
    _ERR_CODE_PARAM_ERR = "Get Parameter Error"
    _ERR_CODE_SERV_ERR = "Server Error"
    _ERR_CODE = {
        _ERR_CODE_ILL_PARAM: 'IllegalParameters',
        _ERR_CODE_PARAM_ERR: 'GetParameterError',
        _ERR_CODE_SERV_ERR: 'ServerError',
    }
    key_rename_map = {
        'chn': 'chn',
        'clientid': 'clientid',
        'appid': 'appid',
        'appname': 'appname',
        'md_id': 'id',
        'md_type': 'type',
        'md_num': 'num',
        'md_appid': 'appid',
        'md_appname': 'appname',
        'md_categid': 'categid',
        'md_categname': 'categname',
        'sd_subjectid': 'subjectid',
        'sd_subjectname': 'subjectname',
        'sd_csubjectid': 'csubjectid',
        'sd_csubjectname': 'csubjectname',
        'log_date': 'log_date',
    }
    db_value_map = {
        '_md_type': 'md_type',
        '_md_appid': 'md_appid',
        '_md_appname': 'md_appname',
        '_md_num': 'md_num',
        '_md_categid': 'md_categid',
        '_md_categname': 'md_categname',
        '_sd_subjectid': 'sd_subjectid',
        '_sd_subjectname': 'sd_subjectname',
        '_sd_csubjectid': 'sd_csubjectid',
        '_sd_csubjectname': 'sd_csubjectname',
        '_log_date': 'log_date',
        '_client_id': 'client_id',
        '_chn': 'chn',
    }
    query_dict = {}
    statist_db = StatistcMongoDB(settings.MONGODB_CONF)
    log_date = timestamp_utc_now()
    try:
        client_id = get_parameter_GET(
            request,
            key_rename_map['clientid'],
            None,
            False,
            0
        )
        chn = get_parameter_GET(
            request,
            key_rename_map['chn'],
            None,
            False,
            0
        )
        md_type = get_parameter_GET(
            request,
            key_rename_map['md_type'],
            None,
            False,
            0
        )
        md_appid = get_parameter_GET(
            request,
            key_rename_map['md_appid'],
            None,
            False,
            0)
        md_appname = get_parameter_GET(
            request,
            key_rename_map['md_appname'],
            None,
            False,
            0
        )
        md_num = get_parameter_GET(
            request,
            key_rename_map['md_num'],
            None,
            False,
            0
        )
        md_categid = get_parameter_GET(
            request,
            key_rename_map['md_categid'],
            None,
            False,
            0
        )
        md_categname = get_parameter_GET(
            request,
            key_rename_map['md_categname'],
            None,
            False,
            0
        )
    except Exception:
        return json_response_error(-1, _ERR_CODE[_ERR_CODE_PARAM_ERR])
    else:
        if md_type not in ('1', '2', '3', '4', '5', '6', '6', '7', '8', '9', '10', '11', '12'):
            return json_response_error(-1, _ERR_CODE[_ERR_CODE_ILL_PARAM])
        if md_type == '8' or md_type == '9':
            try:
                sd_subjectid = get_parameter_GET(
                    request,
                    key_rename_map['sd_subjectid'],
                    None,
                    False,
                    0,
                )
                sd_subjectname = get_parameter_GET(
                    request,
                    key_rename_map['sd_subjectname'],
                    None,
                    False,
                    0
                )
                sd_csubjectid = get_parameter_GET(
                    request,
                    key_rename_map['sd_csubjectid'],
                    None,
                    False,
                    0
                )
                sd_csubjectname = get_parameter_GET(
                    request,
                    key_rename_map['sd_csubjectname'],
                    None,
                    False,
                    0
                )
            except Exception:
                return json_response_error(-1, _ERR_CODE[_ERR_CODE_PARAM_ERR])
            else:
                query_dict = {
                    db_value_map['_md_type']: md_type,
                    db_value_map['_md_appid']: md_appid,
                    db_value_map['_md_appname']: md_appname,
                    db_value_map['_md_num']: md_num,
                    db_value_map['_md_categid']: md_categid,
                    db_value_map['_md_categname']: md_categname,
                    db_value_map['_sd_subjectid']: sd_subjectid,
                    db_value_map['_sd_subjectname']: sd_subjectname,
                    db_value_map['_sd_csubjectid']: sd_csubjectid,
                    db_value_map['_sd_csubjectname']: sd_csubjectname,
                    db_value_map['_log_date']: log_date,
                    db_value_map['_client_id']: client_id,
                    db_value_map['_chn']: chn,
                }
        else:
            query_dict = {
                db_value_map['_md_type']: md_type,
                db_value_map['_md_appid']: md_appid,
                db_value_map['_md_appname']: md_appname,
                db_value_map['_md_num']: md_num,
                db_value_map['_md_categid']: md_categid,
                db_value_map['_md_categname']: md_categname,
                db_value_map['_log_date']: log_date,
                db_value_map['_client_id']: client_id,
                db_value_map['_chn']: chn,
            }
        try:
            if not statist_db.insert_to_StatisticDB(query_dict):
                return json_response_error(-1, _ERR_CODE[_ERR_CODE_SERV_ERR])
        except Exception:
            return json_response_error(-1, _ERR_CODE[_ERR_CODE_SERV_ERR])
        else:
            return json_response_ok()
    finally:
        query_dict.clear()