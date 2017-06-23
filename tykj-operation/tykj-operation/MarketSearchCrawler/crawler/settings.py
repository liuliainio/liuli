#-*- coding: utf-8 -*-
'''
Created on Sep 12, 2013

@author: gmliao
'''
import platform


DEBUG = True


if platform.node() in ['gmliaovm']:
    from crawler.settings_dev import *
elif platform.node() in ['ip-10-134-6-128']:
    from crawler.settings_diandian_international import *
else:
    from crawler.settings_online import *




