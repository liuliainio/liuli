# Django settings for estoreservice project.

import os
import re
from utils import FreeConfigParser

LOG_ROOT = None
DEBUG = True
TEMPLATE_DEBUG = DEBUG
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
UPLOAD_ROOT = None
UPLOAD_FILE_TYPE = None
MONGODB_CONF = None
APK_HOST = None
CDN_APK_HOST = None
IMAGE_HOST = None
SERVICE_HOST = None
SITE_DOMAIN = None
Z_IMAGE_HOST = None
UPLOAD_FILE_ROOT = '/var/app/enabled/operation-webfront/static/'
TEST_ASK_TO_DROP_TEST_MONGODB = False


def _load_config(section, config_files):
    global DEBUG, LOG_ROOT, LANGUAGE_CODE, DATABASES, UPLOAD_ROOT, UPLOAD_FILE_TYPE, MONGODB_CONF, APK_HOST, \
        CDN_APK_HOST, IMAGE_HOST, Z_IMAGE_HOST, SERVICE_HOST, SITE_DOMAIN, UPLOAD_FILE_ROOT

    cp = FreeConfigParser()
    cp.read(config_files)

    DEBUG = cp.getboolean(section, 'debug')
    SITE_DOMAIN = cp.get(section, 'file_storage_domain_conf')
    LOG_ROOT = cp.get(section, 'log_root')
    UPLOAD_ROOT = cp.get(section, 'upload_root')
    UPLOAD_FILE_TYPE = cp.get(section, 'file_type')
    LANGUAGE_CODE = cp.get(section, 'language_code')
    db_conf = re.split(r'[@:/]', cp.get(section, 'db_conf'))
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'USER': db_conf[0],
            'PASSWORD': db_conf[1],
            'HOST': db_conf[2],
            'PORT': db_conf[3],
            'NAME': db_conf[4],
        }
    }
    MONGODB_CONF = cp.get(section, 'mongodb_conf')
    APK_HOST = cp.get(section, 'apk_host')
    CDN_APK_HOST = cp.get(section, 'cdn_apk_host')
    IMAGE_HOST = cp.get(section, 'image_host')
    Z_IMAGE_HOST = cp.get(section, 'z_image_host')
    SERVICE_HOST = cp.get(section, 'service_host')
    UPLOAD_FILE_ROOT = cp.get(section, 'upload_file_root')

_load_config('service', [os.path.join(SITE_ROOT, "estoreservice.cfg")])

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

# DATABASES = {
    #'default': {
        # 'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        # 'NAME': '',                      # Or path to database file if using sqlite3.
        # 'USER': '',                      # Not used with sqlite3.
        # 'PASSWORD': '',                  # Not used with sqlite3.
        # 'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        # 'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    #}
#}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Shanghai'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

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

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

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
SECRET_KEY = 'yda%ei_3djh3667pxcasomd!(p1+v@4blr&t-&5ue#)_f%$)f6'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    #    'estoreservice.middleware.LogMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'estoreservice.urls'

TEMPLATE_DIRS = (
    os.path.join(SITE_ROOT, "templates"),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    #'django.contrib.auth',
    #'django.contrib.contenttypes',
    #'django.contrib.sessions',
    #'django.contrib.sites',
    #'django.contrib.messages',
    #'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    #'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    #'django.contrib.admindocs',
    'estoreservice.api',
    'estoreservice.openapi',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOG_FILE = os.path.join(LOG_ROOT, 'info.log')
LOG_ERR_FILE = os.path.join(LOG_ROOT, 'error.log')
LOG_PERF_FILE = os.path.join(LOG_ROOT, 'perf.log')
LOG_UPLOADAPPLIST = os.path.join(LOG_ROOT, 'uploadapplist.log')
LOG_OPENAPI = os.path.join(LOG_ROOT, 'openapi.log')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
        'detail': {
            'format':
            '%(levelname)s %(asctime)s %(name)s [%(module)s.%(funcName)s] %(message)s',
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
        'pref_file': {
            'level': 'INFO',
            'formatter': 'simple',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': LOG_PERF_FILE,
        },
        'uploadapplist': {
            'level': 'INFO',
            'formatter': 'detail',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': LOG_UPLOADAPPLIST,
        },
        'openapi': {
            'level': 'INFO',
            'formatter': 'detail',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': LOG_OPENAPI,
        },

    },
    'loggers': {
        'unit_test': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django': {
            'handlers': ['console', 'file', 'err_file', ]
            if DEBUG else ['file', 'err_file', ],
            'level': 'INFO',
            'propagate': True,
        },
        'estoreservice': {
            'handlers': ['console', 'file', 'err_file', ]
            if DEBUG else ['file', 'err_file', ],
            'level': 'INFO',
            'propagate': True,
        },
        'estorecore': {
            'handlers': ['console', 'file', 'err_file', ]
            if DEBUG else ['file', 'err_file', ],
            'level': 'INFO',
            'propagate': True,
        },
        'estoreservice.profiling': {
            'handlers': ['pref_file', ],
            'level': 'INFO',
            'propagate': False,
        },
        'uploadapplist': {
            'handlers': ['console', 'uploadapplist']
            if DEBUG else ['uploadapplist'],
            'level': 'INFO',
            'propagate': True,
        },
        'estoreservice.openapi': {
            'handlers': ['console', 'openapi'] if DEBUG else ['openapi'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}
