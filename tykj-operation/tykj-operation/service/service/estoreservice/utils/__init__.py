import datetime
import time
from ConfigParser import SafeConfigParser, NoOptionError, NoSectionError


def flatten_dict(dct):
    if not dct:
        return None
    return dict([(str(k), dct.get(k)) for k in dct.keys()])


def unix_time(value=None):
    if not value:
        value = datetime.datetime.utcnow()
    try:
        return int(time.mktime(value.timetuple()))
    except AttributeError:
        return None


def unixnow():
    '''
    Returns current UNIX timestamp in milliseconds.
    '''
    return long(time.time() * 1000)


def date_today(package):
    if package.find('.en_') >= 0:
        return (
            (datetime.datetime.utcnow() -
             datetime.timedelta(hours=8)).strftime('%Y-%m-%d')
        )
    else:
        return (
            (datetime.datetime.utcnow() +
             datetime.timedelta(hours=8)).strftime('%Y-%m-%d')
        )


class FreeConfigParser(SafeConfigParser):

    def _get(self, section, conv, option, default):
        return conv(self.get(section, option, default=default))

    def get(self, section, option, raw=False, vars=None, default=None):
        try:
            return SafeConfigParser.get(self, section, option, raw, vars)
        except (NoSectionError, NoOptionError) as err:
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
        except (NoSectionError, NoOptionError) as err:
            if default is not None:
                return default
            raise err
