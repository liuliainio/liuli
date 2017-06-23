# -*- coding: utf-8 -*-
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from estorecore.servemodels.update import UpdateMongodbStorage
from estoreservice.utils.utils import json_response, combine_url
from estoreservice.api.utils import get_parameter_GET

update_db = UpdateMongodbStorage(settings.MONGODB_CONF)


@require_GET
@json_response
def update_service(request):
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
    # md: device model
    device_model = get_parameter_GET(request, 'md', required=False)
    client_id = get_parameter_GET(request, 'clientid', required=False)
    rom = get_parameter_GET(request, 'rom', required=False)
    partner = get_parameter_GET(
        request,
        'partner',
        required=False,
        default=u'xianxia')
    broker = get_parameter_GET(request, 'broker', required=False, default=u'')

    for q in (pn, src, vn):
        if isinstance(q, HttpResponse):  # convert failed
            return q

    result = update_db.get_update(
        pn, src, vn, is_auto=auto, device_id=did, os=os,
        os_version=osvn, resolution=re, cpu=cpu, device_model=device_model, rom=rom, client_id=client_id, chn=partner)

    if result is not None:
        if 'download_link' in result:
            result['download_url'] = result['download_link']
        if 'download_url' in result:
            result['download_url'] = combine_url(
                settings.APK_HOST,
                result['download_url'])
    return result
