# Create your views here.
import simplejson as json
from decimal import Decimal
from django.utils.translation import ugettext as _
from django.http import HttpResponse
from estoreoperation.utils import json_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response
from estorecore.datasync.sync_app import sync_obj
from estoreoperation.app.models import *


@json_response
def get_list(request):
    request_get = request.GET
    method = request_get.get('method', '')
    if method == '':
        return
    try:
        app_item = json.loads(request_get.get('app_list', ''))
    except Exception:
        app_item = ''
    if app_item == '':
        return 'input errr'
    sucess_count = 0
    error_count = 0
    apps = Application.objects.filter(package_name__in=app_item)

    if method == 'getInfo':
        package_info = []
        package_info.append(['', 'id', _('name'), _('current_version_name'), _('category_name'), _('sub_category_name'), _('clicks_count'), \
                _('downloads_count'), _('is_published'), _('sync_status')])
        for app in apps:
            package_info.append([app.package_name, app.id, app.name, app.current_version_name, \
                    app.category.name, app.sub_category_name().name, app.clicks_count, app.downloads_count, \
                    _('true') if app.published else _('false'), _('true') if app.sync_status else _('false')])
        return package_info if package_info else ''
    else:
        risk_app = request_get.get('risk_list', '')
        risk_apps = Application.objects.filter(package_name__in=risk_app)
        apps.update(published=0, sync_status=0)
        for app in apps:
            try:
                sync_obj(app, Application)
            except Exception:
                error_count = error_count + 1
                continue
            sucess_count = sucess_count + 1
        risk_apps.update(review_status=2, tag=2)
        return sucess_count


@login_required
def quick_offline(request):
    return render_to_response('offline.html', {}, context_instance=RequestContext(request))
