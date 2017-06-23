from estoreservice.api.errors import parameter_error


def _convert_func(func):
    def wrapper(*args, **kwargs):
        if func == bool:
            return bool(int(*args, **kwargs))
        return func(*args, **kwargs)
    return wrapper


def _get_parameter(request, query_dict, name, convert_func=None,
                   required=True, default=None, alternative_name=None, str_max_length=None):
    item = query_dict.get(name, None)
    if item is None and alternative_name is not None:
        item = query_dict.get(alternative_name, None)
    if item is None and default is not None:
        item = default

    if required and item is None:
        return parameter_error(request, name)

    if item is not None:
        if str_max_length is not None and isinstance(item, str) and len(item) > str_max_length:
            item = item[0: str_max_length]
        if convert_func:
            try:
                item = _convert_func(convert_func)(item)
            except:
                return parameter_error(request, name)
    return item


def get_parameter_GET(request, name, convert_func=None, required=True,
                      default=None, alternative_name=None, str_max_length=None):
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


def get_parameter_POST(request, name, convert_func=None, required=True,
                       default=None, alternative_name=None, str_max_length=None):
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


def get_parameter_META(request, name, convert_func=None, required=True,
                       default=None, alternative_name=None, str_max_length=None):
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


def get_parameter_POST_or_GET(
        request, name, convert_func=None, required=True,
        default=None, alternative_name=None, str_max_length=None):
    value = get_parameter_POST(
        request,
        name,
        convert_func=convert_func,
        required=False,
        default=None,
        alternative_name=alternative_name)
    if value is None:
        value = get_parameter_GET(
            request,
            name,
            convert_func=convert_func,
            required=required,
            default=default,
            alternative_name=alternative_name)
    return value
