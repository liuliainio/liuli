
from estoreservice.openapi.errors import parameter_error


def _convert_func(func):
    def wrapper(*args, **kwargs):
        if func == bool:
            return bool(int(*args, **kwargs))
        return func(*args, **kwargs)
    return wrapper


def _get_parameter(request, query_dict, name, convert_func=None,
                   required=True, default=None, alternative_name=None):
    item = query_dict.get(name, None)
    if item is None and alternative_name is not None:
        item = query_dict.get(alternative_name, None)
    if item is None and default is not None:
        item = default

    if required and item is None:
            return parameter_error(request, name)
    if convert_func and item is not None:
            try:
                item = _convert_func(convert_func)(item)
            except:
                return parameter_error(request, name)
    return item


def get_parameter_GET(request, name, convert_func=None,
                      required=True, default=None, alternative_name=None):
    return (
        _get_parameter(
            request,
            request.GET,
            name,
            convert_func=convert_func,
            required=required,
            default=default,
            alternative_name=alternative_name)
    )


def get_parameter_POST(request, name, convert_func=None,
                       required=True, default=None, alternative_name=None):
    return (
        _get_parameter(
            request,
            request.POST,
            name,
            convert_func=convert_func,
            required=required,
            default=default,
            alternative_name=alternative_name)
    )


def get_parameter_META(request, name, convert_func=None,
                       required=True, default=None, alternative_name=None):
    return (
        _get_parameter(
            request,
            request.META,
            name,
            convert_func=convert_func,
            required=required,
            default=default,
            alternative_name=alternative_name)
    )
