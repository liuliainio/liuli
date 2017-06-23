import sys
import traceback
import logging
from utils.utils import json_response_error
from utils.resp_code import UNKNOWN_ERROR

logger = logging.getLogger(__name__)


def exception_handled(func):

    def _view(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        except Exception:
            exc_type, value, tb = sys.exc_info()
            formatted_tb = traceback.format_tb(tb)
            exception_message = 'An error occurred %s: %s traceback=%s' % (
                exc_type,
                value,
                formatted_tb)
            logger.error(exception_message)

            return json_response_error(UNKNOWN_ERROR)

    return _view
