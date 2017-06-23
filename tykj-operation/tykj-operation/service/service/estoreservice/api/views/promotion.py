import logging
from django.conf import settings
from django.utils import simplejson
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from estorecore.servemodels.promotion import PromotionMongodbStorage
from estoreservice.utils.utils import json_response, append_icon_host
from estoreservice.api.utils import get_parameter_GET, get_parameter_POST, get_parameter_META

logger = logging.getLogger('estoreservice')

promotion_db = PromotionMongodbStorage(settings.MONGODB_CONF)


@require_GET
@json_response
def activities(request):
    client_id = get_parameter_GET(request, 'clientid')
    belong_to = get_parameter_GET(request, 'belong_to')
    start_index = get_parameter_GET(request, 'start_index', convert_func=int)
    count = get_parameter_GET(request, 'count', convert_func=int)
    for q in (client_id, belong_to, start_index, count):
        if isinstance(q, HttpResponse):    # convert failed
            return q

    results = promotion_db.query_activities(
        belong_to,
        start_index=start_index,
        count=count)
    logger.info('activities, client_id=%s, results=%s'
                % (client_id, str([result['id'] for result in results])))

    return append_icon_host(results)


@require_GET
@json_response
def login_pictures(request):
    return append_icon_host(promotion_db.query_login_pictures())


@json_response
def feedbacks(request, types=None):
    if get_parameter_GET(request, 'is_unload', required=False, default=False):
        uni_token = get_parameter_GET(
            request,
            'uni_token',
            required=False,
            default=False)
        if(uni_token):
            feedback = {
                'feedback_str': get_parameter_GET(
                    request,
                    'call_back_str',
                    required=False,
                    default=u'')}
            feedback['uni_token'] = uni_token
            feedback['user_submit'] = True
            feedback['feedback_id'] = get_parameter_GET(
                request,
                'call_back_order',
                required=False,
                default=u'')
            promotion_db.save_uninstall_feedbacks([feedback])
        else:
            client_id = ''
            feedback = {
                'content': get_parameter_GET(
                    request,
                    'call_back_str',
                    required=False,
                    default=u'')}
            feedback['client_id'] = ''
            feedback['source'] = get_parameter_GET(
                request,
                'source',
                required=False,
                default='unload')
            promotion_db.save_feedbacks([feedback])
            logger.info('unload_feedbacks, feedback=%s'
                        % feedback['content'])
        return {'ok': True}

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
        source = get_parameter_GET(
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
    for q in (client_id, feedback, ip):
        if isinstance(q, HttpResponse):    # convert failed
            return q

    feedback['client_id'] = client_id
    feedback['source'] = source
    promotion_db.save_feedbacks([feedback])
    logger.info('feedbacks, client_id=%s, ip=%s' % (client_id, ip))

    return {'ok': True}
