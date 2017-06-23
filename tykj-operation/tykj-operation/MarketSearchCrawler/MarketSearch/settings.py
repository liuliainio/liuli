from platform import node
from scrapy.settings.default_settings import COOKIES_ENABLED

if node() in ['ubuntu', 'test-crawler']:
    from settings_dev import *
elif node() in ['gmliaovm']:
    from settings_gmliao import *
elif node() in ['ct-182-140-141-11.ctappstore',
                'ct-182-140-141-12.ctappstore',
                'ct-182-140-141-13.ctappstore',
                'ct-182-140-141-14.ctappstore',
                'ct-182-140-141-55.ctappstore',
                'ct-182-140-141-56.ctappstore',
                'ct-182-140-141-57.ctappstore',
                'ct-182-140-141-58.ctappstore',
                'ct-182-140-141-59.ctappstore',
                'ct-182-140-141-60.ctappstore',
                'ct-182-140-141-61.ctappstore', ]:
    from settings_prod import *
elif node() in ['ip-10-134-6-128', ]:
    from settings_diandian_international import *
else:
    raise Exception("node:s isn't properly configured for development or production usage." % node())

BOT_NAME = 'MarketSearch'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['MarketSearch.spiders.impl']
NEWSPIDER_MODULE = 'MarketSearch.spiders'

DEFAULT_ITEM_CLASS = 'MarketSearch.items.AppItem'
#USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)
USER_AGENT = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_2; en-US) AppleWebKit/533.3 (KHTML, like Gecko) Chrome/5.0.354.0 Safari/533.3'

ITEM_PIPELINES = ['MarketSearch.pipeline.AppItemAdapterPipeline',
                  #'MarketSearch.pipeline.AppIconPipeline',
                  #'MarketSearch.pipeline.AppImagesPipeline',
                  'MarketSearch.pipeline.AppItemStorePipeline',
                  #'MarketSearch.pipeline.AppItemQueueImagePipeline'
                  ]

EXTENSIONS = {
    #'MarketSearch.extension.DontCloseSpiderExtension':500,
    'scrapy.webservice.WebService': None,
    'scrapy.telnet.TelnetConsole': None,
}

DOWNLOADER_MIDDLEWARES = {'MarketSearch.middleware.RedirectMiddleware': 600,
                          'scrapy.contrib.downloadermiddleware.redirect.RedirectMiddleware': None, }

#DOWNLOAD_DELAY = 3

SPIDER_MIDDLEWARES = {
    'MarketSearch.middleware.HttpErrorMiddleware': 700,
    'scrapy.contrib.spidermiddleware.httperror.HttpErrorMiddleware': None, }

DATA_DIR = '/tmp'

#IDLE_TIME = 1

#LOG_ENABLED = True
#LOG_LEVEL = 'ERROR'
#LOG_FILE = 'log.txt'

IMAGES_STORE = DATA_DIR + '/img/'
IMAGES_EXPIRES = 180
# IMAGES_THUMBS = {
#     'small': (50, 50),
#}

DEFAULT_REQUEST_HEADERS = {'Accept-Language': 'en'}

TELNETCONSOLE_ENABLED = True

COOKIES_ENABLED = True
