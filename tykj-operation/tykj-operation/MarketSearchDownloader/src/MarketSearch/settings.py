'''
Created on Aug 7, 2011

@author: yan
'''
from platform import node


DEP_MODE_LOCAL = 0
DEP_MODE_LOCAL_GMLIAO = 1
DEP_MODE_CTAPPSTORE = 10
DEP_MODE_DIANDIAN_INTERNATIONAL = 20
DEP_MODE = -1

logger = None

if node() in ['ubuntu']:
    from settings_dev import *
    DEP_MODE = DEP_MODE_LOCAL
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
    DEP_MODE = DEP_MODE_CTAPPSTORE
elif node() in ['ip-10-134-6-128']:
    from settings_diandian_international import *
    DEP_MODE = DEP_MODE_DIANDIAN_INTERNATIONAL
else:
    raise Exception("node:s isn't properly configured for development or production usage." % node())
