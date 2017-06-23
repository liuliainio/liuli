#! -*- coding: utf-8 -*-
import logging
import datetime
import simplejson as json
from django.db.models import F
from django.db import connections, transaction
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.views.decorators.http import require_POST

from estorecore.utils.verify_code import Code
from estorecore.models.constants import APP_LABELS
from estorecore.db import timestamp2datetime
from estoreoperation.utils import json_response
from estoreoperation.app.models import *
from estoreoperation.push.models import *
from estoreoperation.search.models import *
from estoreoperation.update.models import *
from estoreoperation.promotion.models import *
from estorecore.datasync.sync_app import sync_single_app


logger = logging.getLogger('estoreoperation')

HASH_EXTRA = 'tianyi'


def check_online_app(download_path):
    av_list = AppVersion.objects.filter(download_path=download_path)
    if av_list:
        av = av_list[0]
        app = av.app
        if app.current_version == av:
            app.sync_status = 0
            app.published = False
            app.save()
            sync_single_app(app)
            return True
    return False


@json_response
def clear_online_app(request):
    download_url = request.GET.get('download_url', '')
    req_hash = request.GET.get('hash', '')
    req_hash = req_hash.strip()
    download_url = download_url.strip()
    info = 'illegal url'
    if download_url and req_hash and len(req_hash)==32:
        import hashlib
        orgin_hash = HASH_EXTRA + download_url + HASH_EXTRA
        m = hashlib.md5(orgin_hash)
        hashed_str = m.hexdigest()
        if hashed_str == req_hash:
            status = check_online_app(download_url)
            if status:
                info = 'find url and cleared'
            else:
                info = 'can not find url'
        else:
            info = 'validate error'
    return info


@json_response
def get_related_lookup_info(request):
    request_get = request.GET
    lookup_cls = request_get.get('cls_name', '')
    lookup_value = request_get.get('v', '')
    if not lookup_cls or not lookup_value:
        logger.exception('Invaild params, url: %s, field: %s, value: %s' % (lookup_cls, lookup_value))
        return ''

    try:
        obj = eval(lookup_cls).objects.get(pk__exact=lookup_value)
        if lookup_cls == 'Application' and (not obj.review_status or not obj.published):
            return 'not_reviewed_app'
    except Exception:
        obj = None
    return str(obj) if obj else ''


@login_required
@json_response
def get_app_detail(request):
    request_get = request.GET
    app_id = request_get.get('app_id', '')

    if app_id =='':
        return []

    is_copy = request_get.get('is_copy','false')
    app_name = request_get.get('app_name','')
    is_copycat = True if is_copy == 'true' else False

    if is_copycat:
        return _copycat_get_app_detail(app_name)
    else:
        return _norm_get_app_detail(app_id)


def _copycat_get_app_detail(app_name):
    cpy_name = _('Is Copycat')
    pkg_name = _('Package Name')
    app_full_name = _('App Name')
    ver_count = _('Version Count')
    ver_code = _('Version Code')
    down_count = _('Download Count')
    app_detail_dict = {'desc':[cpy_name,pkg_name,app_full_name,ver_count,ver_code,down_count]}
    try:
        apps = Application.objects.filter(name__exact=app_name).order_by('-is_copycat')
        app_list = [[app.is_copycat ,app.name , app.package_name , app.versions_count , app.current_version.version , \
                app.downloads_count] for app in apps]
        app_detail_dict.update({'data':app_list})
    except Exception:
        return {}

    return app_detail_dict


def _norm_get_app_detail(app_id):
    try:
        app = Application.objects.get(id=app_id)
    except Exception:
        return []
    app_trans = {('id',1): 'app.id',
                 (_('name'),2): 'app.name',
                 (_('package_name'),3): 'app.package_name',
                 (_('sub_category_name'),4): 'app.sub_category_name().name',
                 (_('modifier'),5): 'app.modifier_name()',
                 (_('modified_time'),6): 'app.modified_time.strftime("%Y-%m-%d %H:%M:%S")',
                 (_('unpublished_reason'),7): 'app.unpublished_reason if app.unpublished_reason else "None"',
            }
    app_detail = [{'name': key[0] + '', 'value': eval(app_trans[key]), 'order': key[1]} for key in app_trans]
    app_detail = sorted(app_detail, key=lambda item: item['order'])

    return app_detail


@login_required
@json_response
def get_package_name(request):
    request_get = request.GET
    try:
        app_item = json.loads(request_get.get('app_list', ''))
    except Exception:
        logger.exception('Invaild param, app_list')
        return ''

    apps = Application.objects.filter(id__in=app_item)
    package_names = {}
    for app in apps:
        package_names[app.id] = app.package_name
    return package_names if package_names else ''


@login_required
@json_response
def sync_applist_add(request):
    request_get = request.GET
    try:
        request_item = json.loads(request_get.get('add_list', ''))
    except Exception:
        return str(_('input error!'))
    list_method = request_item['list_method']
    if request_item['method'] == 'preview':
        items = request_item['app_list']
        return_item = {'exist': {}}
        if list_method == 'TopApp':
            try:
                page_kind = request_item['listKind'].strip()
            except Exception:
                return [False, 'listKind']
            list_category = Category.objects.filter(name=page_kind)
            apps = Application.objects.filter(package_name__in=items, category=list_category[0])
        else:
            apps = Application.objects.filter(package_name__in=items)
        for i, app in enumerate(apps):
            return_item['exist'][app.id] = {'package_name': app.package_name, 'name': app.name}

        if list_method == 'CategoryRecommendApp':
            page_type = request_item['listType']
            exist_apps = CategoryRecommendApp.objects.filter(app__in=apps, type=page_type)
        elif list_method == 'AppListItem':
            app_lists = AppList.objects.filter(name=request_item['list_name'])
            exist_apps = AppListItem.objects.filter(app__in=apps, app_list=app_lists[0])
        else:
            middle_obj = eval(list_method + '.objects')
            exist_apps = middle_obj.filter(app__in=apps)

        for i, item in enumerate(exist_apps):
            return_item['exist'][item.app.id]['order'] = item.order
        return return_item
    else:
        insert_len = request_item['insert']
        if insert_len == 0:
            return [True]
        user = request.user
        now = datetime.datetime.now()

        id_items = [item['id'] for item in request_item['add_app_list']]
        order_items = [item['order'] for item in request_item['add_app_list']]
        apps = Application.objects.filter(id__in=id_items)
        if list_method == 'CategoryRecommendApp':
            page_type = request_item['listType']
            CategoryRecommendApp.objects.filter(type=page_type).update(order=F('order') + insert_len)
            for i, app in enumerate(apps):
                add_item = CategoryRecommendApp(app=app, type=page_type, pub_date=now, creator=user, modifier=user, \
                        created_time=now, modified_time=now, order=order_items[i])
                add_item.review_status = 1
                add_item.published = 1
                add_item.save()
        elif list_method == 'AppListItem':
            app_lists = AppList.objects.filter(name=request_item['list_name'])
            AppListItem.objects.filter(app_list=app_lists[0]).update(order=F('order') + insert_len)
            for i, app in enumerate(apps):
                add_item = AppListItem(app=app, app_list=app_lists[0], creator=user, modifier=user, \
                        created_time=now, modified_time=now, order=order_items[i])
                add_item.review_status = 1
                add_item.published = 1
                add_item.save()
        else:
            middle_obj = eval(list_method)
            middle_obj.objects.all().update(order=F('order') + insert_len)
            for i, app in enumerate(apps):
                add_item = middle_obj(app=app, creator=user, modifier=user, created_time=now, \
                        modified_time=now, order=order_items[i])
                add_item.review_status = 1
                add_item.published = 1
                add_item.save()
        u_id_items = [item['id'] for item in request_item['update_app_list']]
        u_order_items = [item['order'] for item in request_item['update_app_list']]
        apps = Application.objects.filter(id__in=u_id_items)
        if list_method == 'CategoryRecommendApp':
            for i, app in enumerate(apps):
                page_type = request_item['listType']
                exist_apps = CategoryRecommendApp.objects.filter(app=app, type=page_type).update(order=u_order_items[i])
        elif list_method == 'AppListItem':
            for i, app in enumerate(apps):
                app_lists = AppList.objects.filter(name=request_item['list_name'])
                exist_apps = AppListItem.objects.filter(app=app, app_list=app_lists[0]).update(order=u_order_items[i])
        else:
            for i, app in enumerate(apps):
                exist_apps = middle_obj.objects.filter(app=app).update(order=u_order_items[i])
        return [True]


INSERT_APP_SQL = """INSERT INTO `app` values("%(Optime)s",%(GoodsId)s,"%(GoodsName)s",%(CategoryId1)s,%(Chargemode)s,%(StoreId)s,
                    %(APId)s,%(AppStatus)s,%(CategoryId2)s,%(CategoryId3)s,%(Price)s,"%(Appurl)s","%(Iconurl)s","%(Appbrief)s","%(Apptag)s",
                    %(Status)s,"%(Lang)s","%(Author)s","%(Prov_Name)s","%(Last_Onsale_datetime)s","%(Test_remark)s","%(Grade)s",%(Min_SDK_Version)s,
                    %(Max_SDK_Version)s,%(New_CategoryId1)s,%(New_CategoryId2)s,%(Down_count)s) ON DUPLICATE KEY UPDATE
                    Optime="%(Optime)s",GoodsName="%(GoodsName)s",CategoryId1=%(CategoryId1)s,Chargemode=%(Chargemode)s,StoreId=%(StoreId)s,
                    APId=%(APId)s,AppStatus=%(AppStatus)s,CategoryId2=%(CategoryId2)s,CategoryId3=%(CategoryId3)s,Price=%(Price)s,Appurl="%(Appurl)s",
                    Iconurl="%(Iconurl)s",Appbrief="%(Appbrief)s",Apptag="%(Apptag)s",Status=%(Status)s,Lang="%(Lang)s",Author="%(Author)s",Prov_Name="%(Prov_Name)s",
                    Last_Onsale_datetime="%(Last_Onsale_datetime)s",Test_remark="%(Test_remark)s",Grade="%(Grade)s",Min_SDK_Version=%(Min_SDK_Version)s,
                    Max_SDK_Version=%(Max_SDK_Version)s,New_CategoryId1=%(New_CategoryId1)s,New_CategoryId2=%(New_CategoryId2)s,Down_count=%(Down_count)s"""

INSERT_PACKAGE_SQL = """INSERT INTO `package` values("%(Timestamp)s",%(PackID)s,%(GoodsId)s,"%(PackName)s",%(PackStatus)s,%(CheckStatus)s,
                    "%(AppSuffix)s",%(FileSize)s,%(isTaskAdv)s,"%(PackVersion)s","%(VersionName)s","%(PackageTitle)s","%(sig)s","%(FileId)s","%(ShortAddr)s",
                    "%(Build_flag)s",%(Net_type)s,%(CopyNo)s) ON DUPLICATE KEY UPDATE
                    Timestamp="%(Timestamp)s",PackName="%(PackName)s",PackStatus=%(PackStatus)s,CheckStatus=%(CheckStatus)s,AppSuffix="%(AppSuffix)s",
                    FileSize=%(FileSize)s,isTaskAdv=%(isTaskAdv)s,PackVersion="%(PackVersion)s",VersionName="%(VersionName)s",PackageTitle="%(PackageTitle)s",
                    sig="%(sig)s",ShortAddr="%(ShortAddr)s",Build_flag="%(Build_flag)s",Net_type=%(Net_type)s,CopyNo=%(CopyNo)s"""

INSERT_FILE_SQL = """INSERT INTO `file` values(%s,%s,"%s") ON DUPLICATE KEY UPDATE File_Url="%s" """

SDK_VERSION_MAPPING = {
    '1.0': 1,
    '1.1': 2,
    '1.5': 3,
    '1.6': 4,
    '2.0': 5,
    '2.0.1': 6,
    '2.1': 7,
    '2.2': 8,
    '2.3': 9,
    '2.3.1': 9,
    '2.3.2': 9,
    '2.3.3': 10,
    '2.3.4': 10,
    '3.0': 11,
    '3.1': 12,
    '3.2': 13,
    '4.0': 14,
    '4.0.3': 15,
    '4.1': 16,
    '4.2': 17,
    '4.3': 18,
}


def _convert_sdk_version(sdk_version):
    if sdk_version != 0 and 'android' in sdk_version.lower():
        sdk_version = sdk_version.lower().replace('android', '').replace(' ', '')

    return SDK_VERSION_MAPPING.get(sdk_version, 0)


@require_POST
@json_response
def sync_tianyi_app(request):
    param_default_values = {
            'Optime': 0, 'GoodsId': 0, 'GoodsName': '', 'CategoryId1': 0, 'Chargemode': 0, 'StoreId': 0, 'APId': 0, \
            'AppStatus': 0, 'CategoryId2': 0, 'CategoryId3': 0, 'Price': 0, 'Appurl': '', 'Iconurl': '', 'Appbrief': '', \
            'Apptag': '', 'Applabel': 0, 'Status': 0, 'Lang': '', 'Author': '', 'Prov_Name': '', 'Last_Onsale_datetime': 0, \
            'Test_remark': '', 'Grade': '', 'Min_SDK_Version': 0, 'Max_SDK_Version': 0, 'New_CategoryId1': 0, 'New_CategoryId2': 0, \
            'Down_count': 0, 'Timestamp': 0, 'PackID': 0, 'PackName': '', 'PackStatus': 0, 'CheckStatus': 0, 'AppSuffix': '', \
            'FileSize': 0, 'isTaskAdv': 0, 'PackVersion': '', 'VersionName': '', 'PackageTitle': '', 'sig': '', 'FileId': 0, \
            'ShortAddr': '', 'Build_flag': '', 'Net_type': 0, 'CopyNo': 0, 'File_Ids': '', 'File_Urls': '',
        }
    app_infos = {}

    try:
        for key in param_default_values.keys():
            param_value = request.POST.get(key, param_default_values[key])
            if key in ('Optime', 'Last_Onsale_datetime', 'Timestamp'):
                param_value = timestamp2datetime(long(param_value), convert_to_local=True)
                if key == 'Last_Onsale_datetime':
                    param_value = param_value.date()
            elif key in ('Min_SDK_Version', 'Max_SDK_Version'):
                param_value = _convert_sdk_version(param_value)
            elif key == 'AppStatus' and param_value == 0:
                param_value = 2
            if isinstance(param_value, str) or isinstance(param_value, unicode):
                param_value = param_value.replace('"', '\\"')
            app_infos[key] = param_value
    except Exception, e:
        logger.exception('parse paramter failed, params: %s, error: %s' % (app_infos, e))
        return {'Resultcode': '01'}    # params error

    tianyi_db = connections['tianyi']
    try:
        cursor = tianyi_db.cursor()
        cursor.execute((INSERT_APP_SQL % app_infos).replace('\n', ''))
        cursor.execute((INSERT_PACKAGE_SQL % app_infos).replace('\n', ''))

        goods_id, file_ids, file_urls = app_infos['GoodsId'], app_infos['File_Ids'].split(','), app_infos['File_Urls'].split(',')
        for i, file_id in enumerate(file_ids):
            cursor.execute((INSERT_FILE_SQL % (goods_id, file_id, file_urls[i], file_urls[i])).replace('\n', ''))
        transaction.commit_unless_managed()
    except Exception, e:
        logger.exception('insert data failed, app_infos: %s, error: %s' % (app_infos, e))
        return {'Resultcode': '02'}    # insert failed

    return {'Resultcode': '00'}


def generate_verify_code(request):
    return Code(request).display()


@json_response
def get_all_app_labels(request):
    return APP_LABELS
