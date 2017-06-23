import datetime
import json
import httplib
import logging
from ConfigParser import SafeConfigParser, NoOptionError, NoSectionError
from django.http import HttpResponse

logger = logging.getLogger('estoreoperation')

EPOCH = datetime.datetime(1970, 1, 1)

ONE_DAY = datetime.timedelta(days=1)


def total_seconds(delta):
    """return total seconds of a time delta."""
    if not isinstance(delta, datetime.timedelta):
        raise TypeError('delta must be a datetime.timedelta.')
    return delta.days * 86400 + delta.seconds + delta.microseconds / 1000000.0


def datetime2timestamp(dt):
    '''
    Converts a datetime object to UNIX timestamp in milliseconds.
    '''
    if isinstance(dt, datetime.datetime):
        timestamp = total_seconds(dt - EPOCH)
        return long(timestamp * 1000)
    return dt


def json_encode_datetime(obj):
    if hasattr(obj, 'utctimetuple'):
        return datetime2timestamp(obj)
    raise TypeError(repr(obj) + " is not JSON serializable")


def json_response(func):
    '''
    Wraps the return value of the parent as a JSON response.
    '''
    def json_responsed(*args, **kwargs):
        try:
            retval = func(*args, **kwargs)
        except Exception, e:
            logger.exception(e)
            retval = []
        if not isinstance(retval, HttpResponse):
            status_code = httplib.OK
            if isinstance(retval, dict) and 'http_status' in retval:
                status_code = retval.pop('http_status')
            content = json.dumps(retval, ensure_ascii=False, default=json_encode_datetime)
            response = HttpResponse(content, content_type='application/json; charset=utf-8', status=status_code)
        else:
            response = retval
        return response

    return json_responsed


class FreeConfigParser(SafeConfigParser):

    def _get(self, section, conv, option, default):
        return conv(self.get(section, option, default=default))

    def get(self, section, option, raw=False, vars=None, default=None):
        try:
            return SafeConfigParser.get(self, section, option, raw, vars)
        except (NoSectionError, NoOptionError), err:
            if default is not None:
                return default
            raise err

    def getint(self, section, option, default=None):
        return self._get(section, int, option, default)

    def getfloat(self, section, option, default=None):
        return self._get(section, float, option, default)

    def getboolean(self, section, option, default=None):
        try:
            return SafeConfigParser.getboolean(self, section, option)
        except (NoSectionError, NoOptionError), err:
            if default is not None:
                return default
            raise err


class string_with_title(str):
    def __new__(cls, value, title):
        instance = str.__new__(cls, value)
        instance._title = title
        return instance

    def title(self):
        return self._title

    __copy__ = lambda self: self
    __deepcopy__ = lambda self, memodict: self


import socket
import logging
import time
from functools import wraps
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

logger = logging.getLogger('estoreoperation')


class ThriftException(Exception):

    def __init__(self, reason=""):
            Exception.__init__(self, "FAIL TO RETRY CONNECTING THRIFT SERVER: %s" % str(reason))


class Transport(object):

    def __init__(self, conn):
        self.conn = conn

    def __enter__(self):
        self.conn.open()

    def __exit__(self, type, value, tb):
        self.conn.close()
        return False    # raise error again


class ThriftConnection(object):

    GROUP = None

    def __init__(self, servers, client_cls, timeout=10000, keepalive=False):
        self.servers = servers
        self.client_cls = client_cls
        self.keepalive = keepalive
        self.timeout = timeout
        self.server = None
        self.host = None
        self.port = None
        self.protocol = None
        self.client = None
        self.transport = None
        self.thrift_exceptions = (TTransport.TTransportException, socket.error, socket.timeout)

    def open(self, retry=5, timeout_ms=None, force=False):
        if not self.transport or force:
            timeout_ms = timeout_ms or self.timeout
            servers_count = len(self.servers)
            count = min(retry, servers_count)

            if count == 0:
                logger.warn('NO SERVERS  -->group: %s, %s:%s ' % (self.GROUP, self.host, self.port))

            retry_count = 1
            while retry_count <= count:
                try:
                    #TODO: investigate BufferedStream perf

                    # Use sequential retry
                    self.server = self.servers[retry_count - 1]
                    self.host = self.server['host']
                    self.port = self.server['port']

                    thrift_socket = TSocket.TSocket(self.host, int(self.port))
                    thrift_socket.setTimeout(timeout_ms)
                    self.transport = TTransport.TBufferedTransport(thrift_socket)
                    self.protocol = TBinaryProtocol.TBinaryProtocolAccelerated(self.transport)
                    self.client = self.client_cls(self.protocol)
                    self.transport.open()
                    logger.info("CONNECTED TO SUCCESS --> %s:%s." % (self.host, self.port))
                    return
                except Exception:
                    logger.exception('CONNECT TO  FAILED --> %s:%s retry: %d' % (self.host, self.port, retry_count))
                retry_count += 1
            raise ThriftException('FAILED TO CONNECT TO THRIFT SERVER --> servers:%s' % (self.servers))

    def reconnect(self, servers):
        logger.info("SERVER LIST CHANGED --> from: %s to: %s" % (self.servers, servers))
        self.servers = servers
        if self.transport:
            self.transport = None
            #if self.transport.isOpen():
                #self.transport.close()
            #self.open()
            logger.info("NEED RECONNECTED")

    def close(self):
        if not self.keepalive:
            if self.transport.isOpen():
                self.transport.close()

    def batch_func_on_list(self, list_arg, func, batch_size=20):
        '''
        Apply function `func` on a list `list_arg` in batch mode with `batch_size` per batch.
        '''
        remain = len(list_arg)
        start = 0

        rows = []
        while remain > 0:
            batch_count = min(remain, batch_size)
            details = func(list_arg[start:start + batch_count])
            rows.extend([detail.__dict__ for detail in details])

            remain -= batch_count
            start += batch_count

        return rows

number_of_retries = 3
wait_between_retries = 0


def retry(func):
    @wraps(func)
    def thrift_call(conn, *args, **kwargs):
        retry_count = number_of_retries
        while retry_count > 0:
            try:
                conn.open(force=True)
                result = func(conn, *args, **kwargs)
                conn.close()
            except conn.thrift_exceptions, e:
                retry_count -= 1
                logger.warn("THRIFT CALL RETRY --> func:%s(%s, %s),error:%s " % (func.__name__, str(args), str(kwargs), e))
                continue
            except Exception:
                raise

            if wait_between_retries:
                time.sleep(wait_between_retries)
            return result
        raise ThriftException('RETRY FUNC FAILED --> func: %s, retry_count: %s' % (func, retry_count))
    return thrift_call


def retry_on_exception(number_of_retries=3, wait_between_retries=0):
    def wrap(func):
        @wraps(func)
        def thrift_call(conn, *args, **kwargs):
            retry_count = number_of_retries
            while retry_count > 0:
                try:
                    conn.open(force=True)
                    result = func(conn, *args, **kwargs)
                    conn.close()
                except conn.thrift_exceptions, e:
                    retry_count -= 1
                    logger.warn("THRIFT CALL RETRY --> func:%s(%s, %s),error:%s " % (func.__name__, str(args), str(kwargs), e))
                    continue
                except Exception:
                    raise

                if wait_between_retries:
                    time.sleep(wait_between_retries)
                return result
            raise ThriftException('RETRY FUNC FAILED --> func: %s, retry_count: %s' % (func, retry_count))
        return thrift_call
    return wrap


def remote_rpc(logger, swallow_error=False, return_value=None):
    def real_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
            except:
                logger.exception("REMOTE RPC: %s, (%s, %s), FAILED: " % (func.__name__, str(args), str(kwargs)))
                if not swallow_error:
                    raise
                return return_value
            logger.info("REMOTE RPC: %s, (%s, %s), RESULT: %s" % (func.__name__, str(args), str(kwargs), str(result)[:200]))
            return result
        return wrapper
    return real_decorator
