# -*- coding: utf-8 -*-
import datetime
import json
import httplib
import logging
import re
import simplejson
import urllib
from bson.objectid import ObjectId
from django.http import HttpResponse
from django.conf import settings
from resp_code import OK
from estoreservice.api.utils import get_parameter_GET

logger = logging.getLogger('estoreservice')

EPOCH = datetime.datetime(1970, 1, 1)

ONE_DAY = datetime.timedelta(days=1)


def total_seconds(delta):
    """return total seconds of a time delta."""
    if not isinstance(delta, datetime.timedelta):
        raise TypeError('delta must be a datetime.timedelta.')
    return delta.days * 86400 + delta.seconds + delta.microseconds / 1000000.0


def datetime2timestamp(dt):
    '''
    Converts a datetime object to UNIX timestamp in milliseconds.
    '''
    if isinstance(dt, datetime.datetime):
        timestamp = total_seconds(dt - EPOCH)
        return long(timestamp * 1000)
    return dt


def json_encode_default(obj):
    if hasattr(obj, 'utctimetuple'):
        return datetime2timestamp(obj)
    if isinstance(obj, ObjectId):
        return None
    raise TypeError(repr(obj) + " is not JSON serializable")


def _skip_object_id(obj):
    if isinstance(obj, (list, tuple)):
        for item in obj:
            _skip_object_id(item)
    if isinstance(obj, dict) and '_id' in obj:
        del obj['_id']


def _detect_request_encoding(request):
    request_encoding = get_parameter_GET(
        request,
        'requestencoding',
        required=False,
        default=None)
    if request_encoding:
        request.encoding = request_encoding


def _data_adapt(request, data):
    return data


SUPPORT_JSONP = True


def json_response(func):
    def json_responsed(request, *args, **kwargs):
        status_code = httplib.OK
        try:
            _detect_request_encoding(request)
            retval = func(request, *args, **kwargs)
        except Exception as e:
            logger.exception(e)
            status_code = httplib.INTERNAL_SERVER_ERROR
            if settings.DEBUG:
                retval = [str(e)]
            else:
                retval = []

        retval = _data_adapt(request, retval)

        if not isinstance(retval, HttpResponse):
            if isinstance(retval, dict) and 'http_status' in retval:
                status_code = retval.pop('http_status')

            _skip_object_id(retval)
            if SUPPORT_JSONP and 'callback' in request.GET:
                callback = request.GET.get('callback', '')
                content = "%s(%s)" % (
                    callback,
                    json.dumps(retval,
                               skipkeys=True,
                               ensure_ascii=False,
                               default=json_encode_default))
            else:
                content = json.dumps(
                    retval,
                    skipkeys=True,
                    ensure_ascii=False,
                    default=json_encode_default)
            response = HttpResponse(
                content,
                content_type='application/json; charset=utf-8',
                status=status_code)
        else:
            response = retval
        return response
    return json_responsed


def json_response_ok(data=None):
    d = {'status': OK, 'data': data}
    return (
        HttpResponse(
            simplejson.dumps(d),
            content_type='application/json; charset=utf-8')
    )


def json_response_error(error_code, msg=None):
    d = {'status': error_code, 'data': msg}
    return (
        HttpResponse(
            simplejson.dumps(d),
            content_type='application/json; charset=utf-8')
    )


def combine_url(host, path):
    if path.startswith('http://') or path.startswith('https://'):
        return path
    return host + path


def build_download_url(client_id, source, app_id):
    query_string = urllib.urlencode(
        {'clientid': client_id,
         'source': source,
         'app_id': app_id})
    return (
        combine_url(
            settings.SERVICE_HOST,
            'api/app/download/app.json') + '?' + query_string
    )


def build_apk_url(download_path):
    return combine_url(settings.CDN_APK_HOST, download_path)


def build_category_apps_url(
        client_id, source, category_id, extra_params=None):
    params = [('clientid', client_id), ('source', source),
              ('cate_id', category_id)]
    if extra_params:
        params += extra_params

    return (
        combine_url(
            settings.SERVICE_HOST,
            'api/app/category/apps.json') + '?' + urllib.urlencode(params)
    )


def build_subject_apps_url(client_id, source, subject_id, extra_params=None):
    params = [('clientid', client_id), ('source', source),
              ('subject_id', subject_id)]
    if extra_params:
        params += extra_params

    return (
        combine_url(
            settings.SERVICE_HOST,
            'api/app/subject/apps.json') + '?' + urllib.urlencode(params)
    )


def build_img_url(url):
    if not url:
        return url
    return combine_url(settings.IMAGE_HOST, url)


def build_zimg_url(url):
    if not url:
        return url
    return combine_url(settings.Z_IMAGE_HOST, url)


def append_icon_host(items, recursive=False, builder_name='img'):
    IMAGE_HOST_MAPPING = {
        'img': build_img_url,
        'zimg': build_zimg_url,
    }
    img_build_method = IMAGE_HOST_MAPPING.get(builder_name, build_img_url)

    if isinstance(items, dict) and 'results' in items and 'total' in items:
        _append_icon_host(items['results'], img_build_method, recursive)
    else:
        _append_icon_host(items, img_build_method, recursive)
    return items


def _append_icon_host(items, build_method, recursive=False):
    if recursive and isinstance(items, dict):
        for key, value in items.iteritems():
            if isinstance(value, dict) and 'icon_url' in value and value['icon_url']:
                value['icon_url'] = build_method(value['icon_url'])
            _append_icon_host(value, recursive)

    if not recursive or isinstance(items, list):
        for item in items:
            if isinstance(item, dict):
                if 'icon_url' in item and item['icon_url']:
                    item['icon_url'] = build_method(item['icon_url'])
                if 'large_icon_url' in item and item['large_icon_url']:
                    item['large_icon_url'] = build_method(item['large_icon_url'])
                if 'path' in item:
                    item['path'] = build_method(item['path'])
                if 'preview_icon_urls' in item:
                    paths = item['preview_icon_urls'].split(',')
                    urls = [build_method(p) for p in paths]
                    item['preview_icon_urls'] = ','.join(urls)
                if recursive:
                    _append_icon_host(item, recursive)

    return items


def reverse_friendly_size(size):
    base = 1
    if size[-1] == 'K':
        base = 1024
    elif size[-1] == 'M':
        base = 1024 * 1024
    size = size[:-1]
    if size == "None":
        size = 0
    return int(float(size) * base)


def to_int_array(s):
    if not str:
        return []
    return [int(i) for i in s.split('|')]


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


def _app_post_process(apps, with_details=False, related_apps_count=0,
                      os=None, screen_size=None, app_db=None):
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

    if with_details and app_db:
        apps = app_db.get_apps_with_details(apps)

    if related_apps_count and app_db:
        apps = app_db.get_related_apps_for_list(apps, related_apps_count)
        for app in apps:
            if 'related_apps' in app:
                append_icon_host(app['related_apps'])

    for app in apps:
        if 'download_count' in app:
            if app['download_count'] >= 10000:
                # TODO: localization
                app['display_download_count'] = u'%d万+' % (app['download_count'] / 10000)
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


def app_post_process(apps, with_details=False, related_apps_count=0,
                     os=None, screen_size=None, app_db=None):
    if not apps:
        return apps
    if isinstance(apps, dict) and 'results' in apps:
        apps['results'] = _app_post_process(
            apps['results'],
            with_details,
            related_apps_count,
            os,
            screen_size,
            app_db=app_db)
    else:
        apps = _app_post_process(
            apps,
            with_details,
            related_apps_count,
            os,
            screen_size,
            app_db=app_db)
    return apps
