import traceback
import logging
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest, HttpResponseServerError
from django.utils import simplejson
from django.conf import settings

_debug = settings.DEBUG


logger = logging.getLogger('estoreservice.openapi')

_ERROR_CODE_RESOURCE_NOT_EXISTS = 'ResourceNotExists'
_ERROR_CODE_PARAMETER_ERROR = 'MissingOrInvaildRequiredQueryParameter'
_ERROR_CODE_INTERNAL_SERVER_ERROR = 'InternalError'
_ERROR_CODE_AUTHORIZATION_FAILED = 'AuthError'

_ERROR_CODE = {
    _ERROR_CODE_AUTHORIZATION_FAILED: 'Authorization Failed.',
    _ERROR_CODE_RESOURCE_NOT_EXISTS: "The specified resource '%s' does not exist, args: %s.",
    _ERROR_CODE_PARAMETER_ERROR: "A required query parameter '%s' was not specified for this request or was specified incorrectly.",
    _ERROR_CODE_INTERNAL_SERVER_ERROR: "The server encountered an internal error.Please retry the request."
}


class HttpResponseUnauthorized(HttpResponse):
    status_code = 401


def _write_error_response(
        response_class, error_code, error_message, log_error=None):
    error = {
        'Code': error_code,
        'Message': error_message
    }
    if _debug and log_error:
        error['Error'] = log_error
    return response_class(simplejson.dumps(error), mimetype='application/json')


def authentication_fail(request, failed_info=None):
    msg = _ERROR_CODE[_ERROR_CODE_AUTHORIZATION_FAILED]
    log_error = 'request:%s, %s' % (request.build_absolute_uri(), failed_info)
    logger.warn(log_error)
    return (
        _write_error_response(
            HttpResponseUnauthorized,
            _ERROR_CODE_AUTHORIZATION_FAILED,
            msg,
            log_error)
    )


def resource_not_exist(request, resource, **karg):
    format = _ERROR_CODE[_ERROR_CODE_RESOURCE_NOT_EXISTS]
    message = format % (resource, karg.__repr__())
    log_error = 'request:%s,%s' % (request.build_absolute_uri(), message)
    logger.warn(log_error)
    return (
        _write_error_response(
            HttpResponseNotFound,
            _ERROR_CODE_RESOURCE_NOT_EXISTS,
            message,
            log_error=log_error)
    )


def parameter_error(request, parameter):
    format = _ERROR_CODE[_ERROR_CODE_PARAMETER_ERROR]
    message = format % parameter
    log_error = 'request:%s,%s' % (request.build_absolute_uri(), message)
    logger.warn(log_error)
    return (
        _write_error_response(
            HttpResponseBadRequest,
            _ERROR_CODE_PARAMETER_ERROR,
            message,
            log_error=log_error)
    )

TEMPLATE_SERVER_ERROR_GET = '%(method)s : %(uri)s, Internal Server Error Info: %(message)s\n%(trace_stack)s'
TEMPLATE_SERVER_ERROR_POST = '%(method)s : %(uri)s, Body = %(body)s, Internal Server Error Info: %(message)s\n%(trace_stack)s'


def internal_server_error(request, error_message=None, exc_info=None):
    message = _ERROR_CODE[_ERROR_CODE_INTERNAL_SERVER_ERROR]
    trace_stack = '\n'.join(traceback.format_exception(*exc_info))
    vars = {
        'method': request.method,
        'body': request.raw_post_data,
        'message': error_message,
        'uri': request.build_absolute_uri(),
        'trace_stack': trace_stack
    }
    template = TEMPLATE_SERVER_ERROR_POST if request.method == 'POST' else TEMPLATE_SERVER_ERROR_GET
    log_error = template % vars
    logger.error(log_error)
    return (
        _write_error_response(
            HttpResponseServerError,
            _ERROR_CODE_INTERNAL_SERVER_ERROR,
            message,
            log_error=log_error)
    )


def empty_array_response(request):
    #logger.warn('request:%s,empty array response' % request.build_absolute_uri())
    return HttpResponse('[]', mimetype='text/plain')
