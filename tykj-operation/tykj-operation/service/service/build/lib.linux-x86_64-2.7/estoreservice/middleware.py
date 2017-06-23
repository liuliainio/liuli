import time
import logging
from django.utils.encoding import smart_unicode
from utils import flatten_dict


class LogMiddleware:

    start = None
    _logger = logging.getLogger(__name__)

    def process_request(self, request):
        self.start = time.time()

    def process_response(self, request, response):
        if not self.start:
            return response

        try:
            path = smart_unicode(request.path)
            proctime = round(time.time() - self.start, 3)
            get = flatten_dict(request.GET)
            post = flatten_dict(request.POST)

            ip = request.META.get('REMOTE_ADDR', u'')
            status_code = response.status_code

            self._logger.info(
                u'%u %s exec_time=%.3fs GET=%s POST=%s IP=%s RESP=%s' %
                (status_code, path, proctime, get, post, ip, ''))

        except Exception as e:
            self._logger(e)

        return response
