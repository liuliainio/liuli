import logging
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from estorecore.servemodels.search import SearchMongodbStorage
from estoreservice.utils.utils import json_response
from estoreservice.api.utils import get_parameter_GET

logger = logging.getLogger('estoreservice')
search_db = SearchMongodbStorage(settings.MONGODB_CONF)
max_search_hot_keywords = 100


@require_GET
@json_response
def search_hot_keywords(request):
    client_id = get_parameter_GET(request, 'clientid')
    start_index = get_parameter_GET(request, 'start_index', convert_func=int)
    count = get_parameter_GET(request, 'count', convert_func=int)
    for q in (client_id, start_index, count):
        if isinstance(q, HttpResponse):
            return q

    if count <= 0:
        return []

    count = min(max_search_hot_keywords, count)
    results = search_db.query_hot_keywords(
        start_index=start_index,
        count=count)
    #logger.info('search_hot_keywords, %s, %s' % (client_id, str([result['keyword'] for result in results])))

    return results


@require_GET
@json_response
def search_apps(request):
    pass
