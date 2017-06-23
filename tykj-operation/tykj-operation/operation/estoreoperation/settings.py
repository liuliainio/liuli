# coding:utf-8
# Django settings for estoreoperation project.
import os
import re
from django.utils.translation import ugettext_lazy as _
from utils import  FreeConfigParser
from estorecore import CORE_LOCALE_PATH, CORE_TEMPLATE_DIRS

LOG_ROOT = None
DEBUG = True
TEMPLATE_DEBUG = DEBUG
LANGUAGE_CODE = 'zh-cn'
LANGUAGES = (
    ('zh-cn', u'简体中文'),
    ('en', 'English'),
)
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
MONGODB_CONF = None
REPORTING_DB_CONF = None
SITE_DOMAIN = None
ENABLE_IMPORT_DATA_MAIL = None
UPLOAD_FILE_ROOT = '/var/app/enabled/operation-webfront/static/'
PATCH_ROOT = None
STATIC_ROOT = None
MNT_ROOT = None

def _load_config(section, config_files):
    global DEBUG, LOG_ROOT, LANGUAGE_CODE, DATABASES, REPORTING_DB_CONF, MONGODB_CONF, SITE_DOMAIN,\
           UPLOAD_FILE_ROOT, ENABLE_IMPORT_DATA_MAIL,PATCH_SERVICE_HOST,MNT_ROOT,STATIC_ROOT

    cp = FreeConfigParser()
    cp.read(config_files)

    DEBUG = cp.getboolean(section, 'debug')
    LOG_ROOT = cp.get(section, 'log_root')
    LANGUAGE_CODE = cp.get(section, 'language_code')
    SITE_DOMAIN = cp.get(section, 'file_storage_domain_conf')
    REPORTING_DB_CONF = cp.get(section, 'reporting_db_conf')
    estore_db_conf = re.split(r'[@:/]', cp.get(section, 'estore_db_conf'))
    market_db_conf = re.split(r'[@:/]', cp.get(section, 'market_db_conf'))
    tianyi_db_conf = re.split(r'[@:/]', cp.get(section, 'tianyi_db_conf'))
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'USER': estore_db_conf[0],
            'PASSWORD': estore_db_conf[1],
            'HOST': estore_db_conf[2],
            'PORT': estore_db_conf[3],
            'NAME': estore_db_conf[4],
        },
        'market': {
            'ENGINE': 'django.db.backends.mysql',
            'USER': market_db_conf[0],
            'PASSWORD': market_db_conf[1],
            'HOST': market_db_conf[2],
            'PORT': market_db_conf[3],
            'NAME': market_db_conf[4],
        },
        'tianyi': {
            'ENGINE': 'django.db.backends.mysql',
            'USER': tianyi_db_conf[0],
            'PASSWORD': tianyi_db_conf[1],
            'HOST': tianyi_db_conf[2],
            'PORT': tianyi_db_conf[3],
            'NAME': tianyi_db_conf[4],
        }
    }
    MONGODB_CONF = cp.get(section, 'mongodb_conf')
    UPLOAD_FILE_ROOT = cp.get(section, 'upload_file_root')
    ENABLE_IMPORT_DATA_MAIL = cp.getboolean(section, 'enable_import_data_mail')
    PATCH_SERVICE_HOST = cp.get(section, 'patch_service_host')
    MNT_ROOT = cp.get(section, 'mnt_root')
    STATIC_ROOT = cp.get(section, 'static_root')

_load_config('operation', [os.path.join(SITE_ROOT, "estoreoperation.cfg")])

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'backend.operation.alert'
EMAIL_HOST_PASSWORD = "backend.P@55word"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
SERVER_EMAIL = EMAIL_HOST_USER
EMAIL_SUBJECT_PREFIX = '[Estore Operation Site Report] '

ADMINS = (
    ('Kun Li', 'kunli@bainainfo.com'),
    ('Wenyuan Wu', 'wywu@bainainfo.com'),
    ('Jianjian Pan', 'jjpan@bainainfo.com'),
    ('Ju Liang', 'jliang@bainainfo.com'),
    ('Guangming Liao', 'gmliao@bainainfo.com'),
)

MANAGERS = ADMINS

FILE_UPLOAD_HANDLERS = (
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
)

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Shanghai'

# date and datetime field formats
DATE_FORMAT = 'Y-m-d'
DATETIME_FORMAT = 'Y-m-d H:i:s'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

LOGIN_URL = "/admin"
# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '/var/app/enabled/operation-webfront/static/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'p$gy)b!z#7+&ue-*_w@^hv7%lvm+^wwh(_zc&m#8ki5*it2u5n'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    "estoreoperation.context_processors.url_name",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.locale.LocaleMiddleware',   # i18n support
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'pagination.middleware.PaginationMiddleware',
)

ROOT_URLCONF = 'estoreoperation.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)
TEMPLATE_DIRS += CORE_TEMPLATE_DIRS

LOCALE_PATHS = (
    os.path.join(SITE_ROOT, "locale"),
)
LOCALE_PATHS += CORE_LOCALE_PATH

INSTALLED_APPS = (
    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    'smart_selects',
    'ajax_select',
    'chart_tools',
    'googlecharts',
    'estorecore.admin',
    'estoreoperation.app',
    'estoreoperation.push',
    'estoreoperation.search',
    'estoreoperation.update',
    'estoreoperation.patch',
    'estoreoperation.promotion',
    'estoreoperation.statistics',
    'estoreoperation.admin',
    'estoreoperation.admin.newapps',
    'estoreoperation.admin.updateapps',
    'estoreoperation.admin.cateapps',
    'estoreoperation.admin.riskapps',
    'estoreoperation.admin.appreviews',
    'estoreoperation.admin.category',
    'estoreoperation.admin.subject',
    'estoreoperation.admin.usermanagement',
    'estoreoperation.admin.applist',
    'estoreoperation.admin.banner',
    'estoreoperation.admin.utilities',
    'estoreoperation.analysis',
    'pagination',
    'estoreoperation.region',
)

AJAX_LOOKUP_CHANNELS = {
    #   pass a dict with the model and the field to search against
    #'app_version': {'model':'app.appversion', 'search_field':'version'},
    'app_version': ('app.lookups', 'AppVersionLookUp'),
    'application': {'model': 'app.application', 'search_field': 'name'},
}
AJAX_SELECT_BOOTSTRAP = True
AJAX_SELECT_INLINES = 'inline'

LEFT_NAV_MODELS = {
    'app': {
            'order': 1,
            'title': _('application management'),
            'models': [
                'estoreoperation.admin.cateapps.*',
                'estoreoperation.admin.riskapps.*',
                'estoreoperation.admin.newapps.*',
                'estoreoperation.admin.appreviews.*',
                'estoreoperation.admin.updateapps.*',
                'estoreoperation.admin.category.*',
                'estorecore.models.app.AppChannelList',
                'estorecore.models.app.AppList',
            ],
            'app_label_order': {    # use to control the order of leftnav
                'cateapps': 1,
                'riskapps': 2,
                'newapps': 3,
                'appreviews': 4,
                'updateapps': 5,
                'category': 6,
                'app': 7,
            }
        },
    'applist': {
            'order': 2,
            'title': _('applist management'),
            'models': [
                'estoreoperation.admin.applist.*',
                'estoreoperation.admin.banner.*',
                'estoreoperation.admin.subject.*',
                'estorecore.models.promotion.LocalEntry',
            ],
            'app_label_order': {
                'applist': 1,
                'banner': 2,
                'subject': 3,
                'promotion': 4,
            }
        },
    'push': {
            'order': 3,
            'title': _('push management'),
            'models': [
                'estorecore.models.push.Message',
                'estorecore.models.promotion.LoginPicture',
            ],
            'app_label_order': {
                'push': 1,
                'promotion': 2,
            }
        },
    'product': {
            'order': 4,
            'title': _('product management'),
            'models': [
                'estorecore.models.search.*',
                'estorecore.models.update.UpdateApp',
                'estorecore.models.promotion.Feedback',
                'django.contrib.admin.models.LogEntry',
                'estoreoperation.admin.usermanagement.*',
            ],
            'app_label_order': {
                'update': 1,
                'search': 2,
                'promotion': 3,
                'admin': 4,
                'usermanagement': 5,
            }
        },
}

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOG_FILE = os.path.join(LOG_ROOT, 'info.log')
LOG_ERR_FILE = os.path.join(LOG_ROOT, 'error.log')
LOG_SCRIPT_FILE = os.path.join(LOG_ROOT, 'script.log')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
        'detail': {
            'format': '%(levelname)s %(asctime)s %(name)s [%(module)s.%(funcName)s] %(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'formatter': 'detail',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': LOG_FILE,
        },
        'err_file': {
            'level': 'ERROR',
            'formatter': 'detail',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': LOG_ERR_FILE,
        },
        'script_file': {
        'level': 'INFO',
        'formatter': 'simple',
        'class': 'logging.handlers.WatchedFileHandler',
        'filename': LOG_SCRIPT_FILE,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'err_file', ] if DEBUG else ['file', 'err_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'estoreoperation': {
            'handlers': ['console', 'file', 'err_file', ] if DEBUG else ['file', 'err_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'estorecore': {
            'handlers': ['console', 'file', 'err_file', ] if DEBUG else ['file', 'err_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'scripts': {
            'handlers': ['console', 'script_file', 'err_file'] if DEBUG else ['script_file', 'err_file'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}
