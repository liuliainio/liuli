OK = 0

UNKNOWN_ERROR = 1
HTTPS_REQUIRED = 2
PARAM_REQUIRED = 3
SAVE_FILE_ERROR = 4


ERROR_CODE_SUCCESS = 0
ERROR_CODE_REWARD_REPETITIVE_LOTTERY = 1
ERROR_CODE_REWARD_COINS_INSUFFICIENT = 2
ERROR_CODE_NO_APP = 3
ERROR_CODE_REWARD_NO_COINS_APP = 4
ERROR_CODE_REWARD_ALREADY_DOWNLOADED_APP = 5


_ERRORS = {
    ERROR_CODE_SUCCESS: 'success',
    ERROR_CODE_REWARD_REPETITIVE_LOTTERY: 'repetitive lottery',
    ERROR_CODE_REWARD_COINS_INSUFFICIENT: 'coins insufficient',
    ERROR_CODE_NO_APP: 'no such app: %s',
    ERROR_CODE_REWARD_NO_COINS_APP: 'app has no coins',
    ERROR_CODE_REWARD_ALREADY_DOWNLOADED_APP: 'has downloaded this app'
}


def _wrapped_data(code, data, *args, **kwargs):
    return {
        'error_code': code,
        'error_message': _ERRORS[code] %
        args if args else _ERRORS[code],
        'data': data,
    }


def error_return(code, data=None, *args, **kwargs):
    return _wrapped_data(code, data, *args, **kwargs)


def success_return(data):
    return _wrapped_data(ERROR_CODE_SUCCESS, data)
