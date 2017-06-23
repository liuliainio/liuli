import urlparse

def friendly_size(size):
    if size >= 1024 * 1024 *1024:
        size = '%sG' % round(size * 1.0 / (1024 * 1024 * 1024),1)
    elif size >= 1024 * 1024:
        size = '%sM' % round(size * 1.0 / (1024 * 1024),1)
    elif size >= 1024:
        size = '%sK' % round(size * 1.0 / 1024, 1)
    else:
        size = '%sB' % size
    parts = size.split('.')
    if len(parts) > 1:
        if parts[1][0] == '0':
            size = parts[0] + parts[1][-1]
        else:
            size = '%s.%s%s' % (parts[0], parts[1][0], parts[1][-1])
    return size


def parse_url(url):
    if url.startswith('http'):
        url = urlparse.urlsplit(url).path[1:]
    return url


def remove_action_prefix(action):
    sub_strs = action.split('_', 1)
    if len(sub_strs) == 2:
        return sub_strs[1]
    return action


def int_to_array(int_v):
    if  int_v == 0:
        return [0]
    array = []
    current_v = 0x1
    while current_v <= int_v:
        if int_v & current_v > 0:
            array.append(current_v)
        current_v = current_v << 1
    return array


def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except Exception:
        return default


class string_with_title(str):
    def __new__(cls, value, title):
        instance = str.__new__(cls, value)
        instance._title = title
        return instance

    def title(self):
        return self._title

    __copy__ = lambda self: self
    __deepcopy__ = lambda self, memodict: self
