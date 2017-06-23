# -*- coding: utf-8 -*-
import logging
import time
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from estorecore.servemodels.push import PushMongodbStorage
from estorecore.servemodels.user import UserMongodbStorage
from estorecore.servemodels.location import LocationMongodbStorage
from estoreservice.utils.utils import json_response, append_icon_host
from estoreservice.utils.targeted_push import select_messages
from estoreservice.api.utils import get_parameter_POST, get_parameter_GET, get_parameter_META
from M2Crypto import BIO, RSA

logger = logging.getLogger('estoreservice')

push_db = PushMongodbStorage(settings.MONGODB_CONF)
user_db = UserMongodbStorage(settings.MONGODB_CONF)
location_db = LocationMongodbStorage(settings.MONGODB_CONF)


MESSAGE_GROUP_PUSH_INTERVAL = 24 * 60 * 60

# USER DATA ENCRYPTION
PRIVATE_KEY_STRING = """-----BEGIN PRIVATE KEY-----
MIICdQIBADANBgkqhkiG9w0BAQEFAASCAl8wggJbAgEAAoGBALvYk9KqpqqNFdY6
jS6YSbhxcWx/UvRh+l+/hRGxbqQ4layPW2y/rryjnsYCGxgnyinCXfQXoNQKqq+L
VLAdksF843AoFSn/XOx5UYdSEglG/yjMoEvpwF3RaoXFeWUsVe0ByN9zs572BOML
UEiU+ueC1kPwPgBwEOj8Mg+fMtolAgMBAAECgYBqtTw8Bx8IcX7/JGHBH1d5hFAH
b0jDdMkTDSvdgiq09UPpM8Kew0DS/iualeWoUiogkL5og+ejrK+Lax3fsd0EPZVF
PtPkcb91jutF20m8s2vIBDZmwx1n+h+5eRlWSa+3n191pM5WGPS4ZTINVHG3IOYk
paThe+rWSfxYXlTXQQJBAOet62VpMciapjLbufgWDMcDhzjBzXbmLiKCJg1lhPnK
mu4502Cmv+OiPYVnOZFb7AdPM/+M9LdBKepbJi0sY9ECQQDPkLGEmtMv6uXfeV2b
VwzPQBNQCa89X6mjgj36XDSeS/dyAwtbgbHLvSabUDwc3uarofq96bTDzfpMB58g
wIoVAkAUAjU+QOOHy7Nm2Qsqndzkoy1efX5dMmvxlwPqTEY7vH+860mSI1SXOD/P
8aZLI4Ey8GgxPd80pHAWSWD2rcrBAkBDWJ9AdzuugHi1WZuVm1j8pb2eaoYBU9im
xMt3QBOSiPNweqxktGALywOLwSy/8VLGvXetxvZv0ZU0tgRbjB1BAkBqqYIb00w5
zTwYxHb/0x3HrpGkt2etYrYdu3US0wo8M5isnCZsiXUg6yEkmYa9J0GIfoSIedzT
JP5vZjl/O8lN
-----END PRIVATE KEY-----
"""

# The encrypted text could be changed time by time, so we need to decrypt
# to compare


def rsa_decrypt(text_base64):
    if not text_base64:
        return ''
    try:
        rsa = RSA.load_key_string(PRIVATE_KEY_STRING)
        input = text_base64.decode('base64')
        decrypted = rsa.private_decrypt(input, RSA.pkcs1_padding)
        return decrypted
    except:
        return ''

###


class SimplePerfCounter(object):

    def __init__(self):
        self.time_start = self._now_ms()
        self.data = []

    def _now_ms(self):
        return long(time.time() * 1000)

    def set(self, name):
        self.data.append('%s:%d' % (name, self._now_ms() - self.time_start))

    def to_str(self):
        return '|'.join(self.data)


def process_push_request(request, the_logger, from_openapi=False):
    print 'check client_id1'
    perf = SimplePerfCounter()
    client_id = get_parameter_POST(request, 'clientid')
    print 'check client_id1end'
    chn = get_parameter_POST(
        request,
        'chn',
        required=False,
        default=None) or get_parameter_POST(
        request,
        'chn',
        required=from_openapi)
    partner = get_parameter_POST(
        request,
        'partner',
        required=False,
        default=u'')
    user_phone = get_parameter_POST(
        request,
        'usrpn',
        required=False,
        default=u'')
    source = get_parameter_POST(request, 'source')
    imei = get_parameter_POST(request, 'imei', required=False, default=u'')
    imsi = get_parameter_POST(
        request,
        'imsi',
        required=False,
        default=u'',
        alternative_name='az')
    device_model = get_parameter_POST(
        request,
        'device_model',
        required=False,
        default=u'')
    device_info = get_parameter_POST(
        request,
        'deviceinfo',
        required=False,
        default=u'')
    os_v = get_parameter_POST(
        request,
        'os',
        convert_func=int,
        required=False,
        default=0)
    screensize = get_parameter_POST(
        request,
        'screen_size',
        required=False,
        default=u'')
    sim_operator = get_parameter_POST(
        request,
        'sim_operator',
        required=False,
        default='0')
    client_version = get_parameter_POST(
        request,
        'client_version',
        convert_func=int,
        required=False,
        default=0)
    print 'check client_id2'
    locale = get_parameter_POST(request, 'locale')
    last_query_time = get_parameter_POST(request, 't', convert_func=long)
    ip = get_parameter_META(
        request,
        'REMOTE_ADDR',
        required=False,
        default=u'')
    count = get_parameter_POST(
        request,
        'count',
        convert_func=int,
        required=False,
        default=5)
    debug = get_parameter_POST(
        request,
        'debug',
        convert_func=int,
        required=False,
        default=0)
    debug_user_tags = get_parameter_POST(
        request,
        'debug_user_tags',
        required=False,
        default=u'')
    print 'check client_id3'
    if not from_openapi and (isinstance(chn, HttpResponse) or not chn) and partner:
        chn = partner
    for q in (chn, client_id, source, locale, last_query_time, ip, client_version, os_v, sim_operator):
        if isinstance(q, HttpResponse):  # convert failed
            logger.error(
                'push_notification_messages, ip=%s, clientid=%s, invalid request, q=%s' %
                (str(ip), str(client_id), str([client_id, source, locale, last_query_time, ip, client_version, os_v, sim_operator])))
            return q

    try:
        if sim_operator == '':
            sim_operator = 0
        else:
            # pick the first sim card if there are more than one. TODO: use all
            sim_operator = int(sim_operator.split(',')[0])
    except Exception as e:
        logger.error(
            'push_notification_messages, ip=%s, clientid=%s, invalid sim_operator, q=%s' %
            (str(ip), str(client_id), str(sim_operator)))
        sim_operator = 0

    if not client_version:
        try:
            #from right to split and max split is 1.
            s = source.rsplit('_', 1)
            if len(s) > 1 and s[1]:
                client_version = int(s[1])
        except Exception as e:
            pass
    if perf:
        perf.set('prms')

    # some clients send milliseconds. convert the ms to seconds
    # detect ms by 100000000000 (which is 11/16/5138 5:46:40 PM in seconds,
    # which is not a valid second value at current time)
    last_query_time_in_seconds = last_query_time if last_query_time < 100000000000 else last_query_time / \
        1000

    black_list = 0
    is_test_device = False
    decrypted_user_phone = rsa_decrypt(user_phone)
    decrypted_imsi = rsa_decrypt(imsi)
    if perf:
        perf.set('dcrypt')
    
    print 'check client_id'
    is_in_blacklist = push_db.in_blacklist(
        client_id,
        decrypted_user_phone,
        imei,
        decrypted_imsi)
    if perf:
        perf.set('blckl')

    print '7384384838283283'
    print is_in_blacklist
    if is_in_blacklist:
        black_list = 1
        results = []
    else:
        is_test_device = push_db.is_test_device(client_id)
        if perf:
            perf.set('tstd')

        results = push_db.query_messages(
            last_query_time_in_seconds,
            client_id,
            locale,
            source=source.split('_')[0],
            is_test_device=is_test_device)
        print 'results is :'
        print results

        if perf:
            perf.set('qm')

    if not device_model and device_info:
        device_model = device_info.rsplit('_', 1)[0]

    final_results = select_messages(
        messages=results,
        client_id=client_id,
        source=source,
        chn=chn,
        is_test_device=is_test_device,
        count=count,
        device_model=device_model,
        os_v=os_v,
        screensize=screensize,
        sim_operator=sim_operator,
        user_phone=user_phone,
        client_version=client_version,
        ip=ip,
        debug=debug,
        debug_user_tags=debug_user_tags,
        perf=perf,
        push_db=push_db,
        user_db=user_db,
        location_db=location_db)

    print 'final_results is:'
    print final_results
    final_results = append_icon_host(final_results, True)
    if perf:
        perf.set('pp')

    the_logger.info('push_notification_messages, chn=%s, ip=%s, clientid=%s, user_phone=%s|%s, source=%s, locale=%s, last_query_time=%s, imei=%s, imsi=%s|%s, rawmessages=%s, finalmessages=%s, blacklist=%s, device_model=%s, os=%d, screensize=%s, sim_operator=%d, client_version=%d, perf=%s'
                    % (str(chn), ip, client_id, user_phone if not decrypted_user_phone else '', decrypted_user_phone, source, locale, last_query_time, imei, imsi if not decrypted_imsi else '', decrypted_imsi, str([result.get('message_id', 0) for result in results]) if debug else '', str([result.get('message_id', 0) for result in final_results]), black_list, device_model, os_v, screensize, sim_operator, client_version, perf.to_str()))

    return final_results


#@require_POST
@json_response
def push_notification_messages(request):
    return process_push_request(request, logger)
