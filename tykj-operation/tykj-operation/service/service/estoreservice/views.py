# -*- coding: utf-8 -*-
import time
import simplejson as json
from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response
from estorecore.servemodels.promotion import PromotionMongodbStorage

promotion_db = PromotionMongodbStorage(settings.MONGODB_CONF)

templates_dict = {
}

channel_dict = {
}


def feedback(request, types=None):
    request_get = request.GET
    usr = request_get.get('usr', '')
    channel_name = request_get.get('cn', None)
    channel_setting = channel_dict.get(channel_name)
    image_name = channel_setting['image_name']
    tml_title = channel_setting['title']

    if usr:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        now = time.time() * 1000
        uit = round(now)
        client_data = {
            'usr': usr,
            'ip': ip,
            'vc': int(request_get.get('vc', 0)),
            'pn': request_get.get('pn', ''),
            'vn': request_get.get('vn', ''),
            'cn': request_get.get('cn', ''),
            'it': int(request_get.get('it', 0)),
            'at': int(request_get.get('at', 0)),
            'device_info': request_get.get('device_info', ''),
            'os': request_get.get('os', ''),
            'model': request_get.get('model', ''),
            'uit': uit
        }
        uni_token = hash(usr + str(uit))
        feedback = {'source': source,
                    'client_id': usr,
                    'content': '',
                    'extras': json.dumps(
                        client_data),
                    'uni_token': str(uni_token)}
        promotion_db.save_uninstall_feedbacks([feedback])
        return (
            render_to_response(
                tml,
                {'uni_token': uni_token,
                 'image_name': image_name,
                 'tml_title': tml_title},
                context_instance=RequestContext(request))
        )
    else:
        return (
            render_to_response(
                tml,
                {'image_name': image_name,
                 'tml_title': tml_title},
                context_instance=RequestContext(request))
        )
