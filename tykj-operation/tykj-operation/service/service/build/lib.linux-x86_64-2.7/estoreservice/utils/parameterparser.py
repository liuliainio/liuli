# -*- coding: utf-8 -*-
import simplejson
from django.http import HttpResponse
from estoreservice.api.errors import parameter_error
from estoreservice.utils.requestparameters import *

PRE_DEFINED_PARAMETERS = [P_CLIENT_ID, P_SOURCE, P_CHN, P_IP]


class _Parsers(object):
    parsers = None

    @staticmethod
    def _convert_func(func):
        def wrapper(*args, **kwargs):
            if func == bool:
                return bool(int(*args, **kwargs))
            return func(*args, **kwargs)
        return wrapper

    @staticmethod
    def _get_parameter(request, query_dicts, name, alternative_names=None,
                       convert_func=None, required=True, default=None, str_max_length=None):
        if alternative_names is not None and isinstance(alternative_names, str):
            alternative_names = [alternative_names]

        item = None
        for query_dict in query_dicts:
            item = query_dict.get(name, None)
            if item is None and alternative_names is not None:
                for alternative_name in alternative_names:
                    item = query_dict.get(alternative_name, None)
                    if item is not None:
                        break
            if item is not None:
                break

        if item is not None:
            if str_max_length is not None and len(item) > str_max_length:
                item = item[0: str_max_length]
        else:
            if default is not None:
                item = default

        if required and item is None:
            return parameter_error(request, name)

        if item is not None:
            if convert_func:
                try:
                    item = _Parsers._convert_func(convert_func)(item)
                except:
                    return parameter_error(request, name)
        return item

    @staticmethod
    def _build_parser(
            name, alternative_names=None, enabled_get=True, enabled_post=True,
            enabled_meta=False, convert_func=None, default=None, str_max_length=None):
        def do_parse(request, required=False, default=default):
            query_dicts = []
            if enabled_post and request.method == 'POST':
                query_dicts.append(request.POST)
            if enabled_get:
                query_dicts.append(request.GET)
            if enabled_meta:
                query_dicts.append(request.META)
            return _Parsers._get_parameter(request, query_dicts, name, alternative_names=alternative_names, convert_func=convert_func, required=required, default=default, str_max_length=str_max_length
                                           )
        return do_parse

    @staticmethod
    def get(param):
        if _Parsers.parsers is None:
            _Parsers.parsers = dict()
            _Parsers.parsers[
                P_CLIENT_ID] = _Parsers._build_parser(
                'clientid',
                str_max_length=255)
            _Parsers.parsers[P_SOURCE] = _Parsers._build_parser(
                'source',
                str_max_length=255)
            _Parsers.parsers[P_CHN] = _Parsers._build_parser(
                'chn',
                str_max_length=255)
            _Parsers.parsers[
                P_DOWNLOAD_URL] = _Parsers._build_parser(
                'download_url',
                str_max_length=4000)
            _Parsers.parsers[
                P_PAGE_URL] = _Parsers._build_parser(
                'page_url',
                str_max_length=4000)
            _Parsers.parsers[P_APP_ID] = _Parsers._build_parser(
                'app_id',
                convert_func=int,
                str_max_length=255)
            _Parsers.parsers[
                P_PACKAGE_NAME] = _Parsers._build_parser(
                'packagename',
                str_max_length=255)
            _Parsers.parsers[P_IS_RENAME] = _Parsers._build_parser(
                'rn',
                convert_func=bool,
                default=True)
            _Parsers.parsers[
                P_VERSION_CODE] = _Parsers._build_parser(
                'versioncode',
                convert_func=int)
            _Parsers.parsers[P_PLATFORM] = _Parsers._build_parser(
                'platform',
                convert_func=int,
                default=1)
            _Parsers.parsers[P_JAILBREAK] = _Parsers._build_parser(
                'jailbreak',
                convert_func=int,
                default=0)
            _Parsers.parsers[
                P_OLD_HASH] = _Parsers._build_parser(
                'old_hash',
                str_max_length=255)
            _Parsers.parsers[P_DISABLE_ME] = _Parsers._build_parser(
                'disableme',
                convert_func=int,
                default=0)
            _Parsers.parsers[P_IP] = _Parsers._build_parser(
                'REMOTE_ADDR',
                default=u'',
                enabled_get=False,
                enabled_post=False,
                enabled_meta=True,
                str_max_length=255)
        return _Parsers.parsers[param]


def _internal_parse_parameter(request, param, required, output_parameters):
    parser = _Parsers.get(param)
    value = parser(request, required=required)
    if isinstance(value, HttpResponse):
        return value
    output_parameters[param] = value
    return None


def _internal_parse_parameters(
        request, input_parameters, required, output_parameters):
    for param in input_parameters:
        if isinstance(param, int):
            ret = _internal_parse_parameter(
                request,
                param,
                required,
                output_parameters)
            if ret is not None:
                return ret
        elif isinstance(param, tuple):
            for p in param:
                ret = _internal_parse_parameter(
                    request,
                    p,
                    False,
                    output_parameters)
                if ret is not None:
                    return ret
            if required and all(output_parameters[p] is None for p in param):
                return (
                    parameter_error(
                        request,
                        'parameter missing: ' + str(param))
                )
        else:
            raise Exception('not supported type of parameter')
    return None


# required_parameters: e.g. [P_CHN, P_CLIENT_ID, (P_PACKAGE_NAME, P_APP_ID)] means: P_CHN and P_CLIENT_ID are required, either P_PACKAGE_NAME or P_APP_ID is required
# optional_parameters: optional parameters, if not given, default avlues will be used
# use_pre_defined_parameters: add the PRE_DEFINED_PARAMETERS to required
# parameters
def parse_parameters(
        required_parameters=[], optional_parameters=[], use_pre_defined_parameters=True):
    def inner_parse_parameters(func):
        def execute(request, *args, **kwargs):
            parameters = dict()

            ret = _internal_parse_parameters(
                request,
                (PRE_DEFINED_PARAMETERS if use_pre_defined_parameters else []) +
                required_parameters,
                True,
                parameters)
            if ret is not None:
                return ret

            ret = _internal_parse_parameters(
                request,
                optional_parameters,
                False,
                parameters)
            if ret is not None:
                return ret

            kwargs['parameters'] = parameters
            return func(request, *args, **kwargs)
        return execute
    return inner_parse_parameters


################## TEST CODE ##############
if __name__ == '__main__':
    class MockRequset:
        GET = {
            'source': 'test_1',
            'client_id': 'clientid_test',
            'chn': 'testchn'}
        POST = {'source': 'test_1'}
        META = {'source': 'test_1'}

    @parse_parameters(required_parameters=[P_DOWNLOAD_URL])
    def test(request, test_param, parameters):
        print 'inner test'
        print 'parameters:', parameters
        return {'test_return': 'OK'}

    request = MockRequset()
    print test(request, 'test_param')
