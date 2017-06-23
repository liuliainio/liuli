# -*- coding: utf-8 -*-
from decimal import Decimal
from django.utils.translation import ugettext_lazy as _
from estorecore.utils.enum import Enum

"""
FOR APPLICATION:
   if t_status = NOT_SET, show us app_id
   if t_status = PUBLISH and t_id, show us t_id
   if t_status = UNPUBLISH and t_id, set app unpublish.

FOR APPVERSION (app.current_version):
   if t_status = NOT_SET or t_status = NEW_THAN_TIANYI, we will sync data to tianyi.
   if t_status in ( PUBLISHED, UNPUBLISHED, EQ_THAN_TIANYI, OLD_THAN_TIANYI ) do nothing.
"""
LOCAL_ENTRY_ACTION = Enum({
    'URL': ('OpenURL', _('open url')),
})

LOCAL_ENTRY_PARAMETER = Enum({
    'PHONE_NUM': ('phone_num', _('phone number')),
    'NONE': ('none', _('none')),
})

TIANYI_PAY_TYPES = Enum({
    'NOT_SET': (0, _('not set')),
    'CPS' : (1,'CPS'),
    'CPT' : (2,'CPT'),
    'CPA' : (3,'CPA'),
})

TIANYI_STATUS = Enum({
    'NOT_SET': (0, _('not set')),
    'PUBLISHED': (1, _('published')),
    'UNPUBLISHED': (2, _('unpublished')),
    'EQ_THAN_TIANYI': (3, _('eq than tianyi')),
    'OLD_THAN_TIANYI': (4, _('old than tianyi')),
    'NEW_THAN_TIANYI': (5, _('new than tianyi')),
    'IN_BLACKLIST': (6, _('in blacklist')),
})

TIANYI_CHARGEMODE = Enum({
    'NOT_SET': (0, _('not set')),
    'BY_TIME': (1, _('by time')),
    'MONTHLY': (2, _('monthly')),
    'TIMELY': (3, _('timely')),
    'FREE': (4, _('free')),
    'CHARGE_TIMELY': (5, _('charge timely')),
    'CHARGE_MONTHLY': (6, _('charge monthly')),
})

APP_LIST_TYPES = Enum({
    'DEFAULT': (0, _('default')),
    # 'SUBJECT': (1, _('subject')),
    'BANNER': (2, _('banner')),
    'GAME_LIST': (3, _('game list')),
})

REVIEWED_DESC_PREVIEW_STATUS = Enum({
    'ALL_NOT_REVIEW':(0,_('all not review')),
    'CURRENT_NOT_REVIEW':(1,_('current not review')),
    'CURRENT_REVIEW':(2,_('current review')),
})

GAME_APP_DISPLAY_MODE = Enum({
    'TOP_AREA_BANNER': (0, _('top area big banner')),
    'DOUBLE_COLUMN_BANNER': (1, _('double column small banner')),
    'SINGLE_COLUMN_BANNER': (2, _('single column middle banner')),
    'DOUBLE_COLUMN_APP': (3, _('double column game app')),
})

APP_TYPES = Enum({
    'DEFAULT': (0, _('default')),
    'JAIL_BREAK': (1, _('jail break')),
    'THEME': (2, _('theme')),
    'WALLPAPER': (3, _('wallpaper')),
})

PLATFORMS = Enum({
    'GENERAL': (0, _('general')),
    'ANDROID_PHONE': (0x1, _('android phone')),
    'ANDROID_PAD': (0x2, _('android pad')),
    'ANDROID_PHONE_PAD': (0x3, _('android phone & pad')),
    'IPHONE': (0x4, _('iphone')),
    'IPAD': (0x8, _('ipad')),
    'IPHONE_IPAD': (0xC, _('iphone & ipad')),
})

BELONGTOS = Enum({
    'CTAPPSTORE': (0, _('CT App Store')),
})

CATEGORY_LEVELS = Enum({
    'CATEGORY': (1, _('Category')),
    'SUB_CATEGORY': (2, _('Sub Category')),
})

APP_SOURCES = Enum({
    'MANUAL': (1, _('Manual')),
    'DEV_UPLOAD': (2, _('Developer uploaded')),
    'CRAWLED': (3, _('Auto crawled')),
    'HIAPK': (4, _('hiapk.com')),
    'GOAPK': (5, _('goapk.com')),
    'NDUOA': (6, _('nduoa.com')),
    'APPCHINA': (7, _('appchina.com')),
    'MUMAYI': (8, _('mumayi.com')),
    'AS_BAIDU': (9, _('as.baidu.com')),
    '360_ZHUSHOU': (10, _('zhushou.360.cn')),
    'WANDOUJIA': (11, _('wandoujia.com')),
    'MYAPP': (12, _('myapp.com')),
})

CRAWLED_SOURCES = {
    "hiapk.com": 4,
    "goapk.com": 5,
    "nduoa.com": 6,
    "appchina.com": 7,
    "mumayi.com": 8,
    "as.baidu.com": 9,
    "zhushou.360.cn": 10,
    "wandoujia.com": 11,
    "myapp.com": 12,
}

APP_TAGS = Enum({
    'UNKNOWN': (0, _('Unknown')),
    'SAFE': (1, _('Safe')),
    'RISK': (2, _('Risk')),
    'TOP': (3, _('Top App')),
    'HOT': (4, _('Hot App')),
    'RECOMMEND': (5, _('Recommend App')),
    'CHARGES': (6, _('Charge App')),
})

RECOMMEND_TYPES = Enum({
    'NEWEST': (10, _('Newest')),
    'HOTTEST': (11, _('Hottest')),
    'MATCHEST': (12, _('Matchest')),
    'HOME_NEW': (13, _('Home new')),
})

APP_RATES = (
    (Decimal('0.0'), '0.0'),
    (Decimal('0.5'), '0.5'),
    (Decimal('1.0'), '1.0'),
    (Decimal('1.5'), '1.5'),
    (Decimal('2.0'), '2.0'),
    (Decimal('2.5'), '2.5'),
    (Decimal('3.0'), '3.0'),
    (Decimal('3.5'), '3.5'),
    (Decimal('4.0'), '4.0'),
    (Decimal('4.5'), '4.5'),
    (Decimal('5.0'), '5.0'),
)

SYNC_STATUS = Enum({
    'NEED_SYNC': (0, _('Need Sync')),
    'SYNCED': (1, _('Synced')),
})

MESSAGE_STATUS = Enum({
    'DISABLED': (0, _('Disabled')),
    'PRE_RELEASE': (1, _('Pre_release')),
    'PUBLISHED': (2, _('Published')),
})

REVIEW_STATUS = Enum({
    'NOT_REVIEWED': (0, _('Not Reviewed')),
    'APPROVED': (1, _('Approved')),
    'REJECTED': (2, _('Rejected')),
})

RICHITEM_TYPE = Enum({
    'NO_CLICKS': (0, _('No Clicks')),
    'EMBEDDED_TEMPLATE': (1, _('Embedded into Website')),
    'WAP': (2, _('WAP')),
    'APP_DETAILES_PAGE': (3, _('App Details Page')),
    'SUBJECT_INFO': (4, _('Subject Information')),
    'URL': (5, _('URL')),
    'TIANYI_KUWAN': (6, _('Tianyi Kuwan')),
    'TIANYI_QNW': (7, _('Tianyi Quan Neng Wan')),
})

ACTIVITY_STATUS = Enum({
    'NO': (0, _('No Status')),
    'HOT': (1, _('Hot')),
    'PICKED': (2, _('Picked')),
    'NEW': (3, _('New')),
})

ACTIVITY_TAGS = Enum({
    'NEWEST': (1, _('Newest')),
    'HOTTEST': (2, _('Hottest')),
    'EXPIRED': (3, _('Expired')),
})

BANNER_IMAGE_AREAS = Enum({
    'TOP': (1, _('Top area')),
    'RECOMMEND': (2, _('Recommend area')),
})

STATS_TAGS = Enum({
    'REAL': (1, _('Real data')),
    'FAKE': (2, _('Fake data')),
})

KUWAN_LIST_TYPES = Enum({
    'ORDER': (0, _('order type')),
    'ON_DEMAND': (1, _('On demand type')),
})

PUSH_MESSAGE_ACTIONS = Enum({
    'URL': ('url', _('URL')),
    'APP_DETAILES_PAGE': ('app_detail_page', _('App Details Page')),
    'SUBJECT_INFO': ('subject_info', _('Subject Information')),
    'SHORT_CUT_DETAIL_PAGE': ('short_cut_detail_page', _('Create Short Cut (Click into app detail page)')),
    'SHORT_CUT_DOWNLOAD_APP': ('short_cut_download_app', _('Create Short Cut (Click to download app)')),
    'SHORT_CUT_URL': ('short_cut_url', _('Create Short Cut (Click to open url)')),
    'DOWNLOAD_APP': ('download_app', _('Download or Launch App')),
    'DOWNLOADB': ('download_background', _('Download app in background')),
    'LAUNCHB': ('launch_background', _('Launch app in background')),
})

COMMON_MESSAGE_ACTIONS = Enum({
    'URL': ('url', _('URL')),
    'APP_DETAILES_PAGE': ('app_detail_page', _('App Details Page')),
    'DOWNLOAD_APP': ('download_app', _('Download or Launch App')),
    'SUBJECT_INFO': ('subject_info', _('Subject Information')),
})

PUSH_MESSAGE_DISPLAY_AREAS = Enum({
    'NOTIFICATION': (0, _('notification')),
    'DIALOG': (1, _('dialog')),
})

UPDATE_BTN_ACTIONS = Enum({
    'UPDATE': ('update', _('Update')),
    'CANCEL': ('cancel', _('Cancel')),
})

TG_DEVICES = Enum({
    'SAMSUNG': ('samsung', _('Samsung')),
    'HUAWEI': ('huawei', _('Huawei')),
    'ZTE': ('zte', _('ZTE')),
    'HTC': ('htc', _('HTC')),
    'MOTOROLA': ('motorola', _('Motorola')),
    'LG': ('lg', _('LG')),
    'LENOVO': ('lenovo', _('Lenovo')),
    'GOOGLE': ('google', _('Google')),
    'XIAOMI': ('xiaomi', _('XIAOMI')),
    'EMULATIONAL': ('emulational', _('Emulational Phone')),
})

TG_SYS_VERSIONS = Enum({
    '2_1': ('2.1', '2.1'),
    '2_2': ('2.2', '2.2'),
    '2_3': ('2.3', '2.3'),
    '4_0': ('4.0', '4.0'),
    '4_1': ('4.1', '4.1'),
})

TG_SCREEN_SIZES = Enum({
    '800_1280': ('800x1280', '800x1280'),
    '720_1280': ('720x1280', '720x1280'),
    '480_854': ('480x854', '480x854'),
    '480_800': ('480x800', '480x800'),
    '320_480': ('320x480', '320x480'),
    '240_320': ('240x320', '240x320'),
})

TG_OPERATORS = Enum({
    'MOBILE': ('46000,46002', _('China Mobile')),
    'UNICOM': ('46001', _('China Unicom')),
    'TELECOM': ('46003', _('China Telecom')),
    'NO_SIM': ('0', _('No Sim')),
})

TG_CITIES = Enum({
    'ANHUI': ('1', _('Anhui')),
    'BEIJING': ('2', _('Beijing')),
    'CHONGQING': ('3', _('Chongqing')),
    'FUJIAN': ('4', _('Fujian')),
    'GANSHU': ('5', _('Ganshu')),
    'GUANGDONG': ('6', _('Guangdong')),
    'GUANGXI': ('7', _('Guangxi')),
    'GUIZHOU': ('8', _('Guizhou')),
    'HAINAN': ('9', _('Hainan')),
    'HEBEI': ('10', _('Hebei')),
    'HEINAN': ('11', _('Heinan')),
    'HEILONGJIANG': ('12', _('Heilongjiang')),
    'HUBEI': ('13', _('Hubei')),
    'HUNAN': ('14', _('Hunan')),
    'JILIN': ('15', _('Jilin')),
    'JIANGSU': ('16', _('Jiangsu')),
    'JIANGXI': ('17', _('Jiangxi')),
    'LIAONING': ('18', _('Liaoning')),
    'NEIMENGGU': ('19', _('Neimenggu')),
    'NINGXIA': ('20', _('Ningxia')),
    'QINGHAI': ('21', _('Qinghai')),
    'SHANDONG': ('22', _('Shandong')),
    'SHANXI': ('23', _('Shanxi')),
    'SHANNXI': ('24', _('Shannxi')),
    'SHANGHAI': ('25', _('Shanghai')),
    'SICHUAN': ('26', _('Sichuan')),
    'TIANJIN': ('27', _('Tianjin')),
    'XIZANG': ('28', _('Xizang')),
    'XINJIANG': ('29', _('Xinjiang')),
    'YUNNAN': ('30', _('Yunnan')),
    'ZHEJIANG': ('31', _('Zhejiang')),
})

TG_GENDERS = Enum({
    'MALE': ('male', _('Male')),
    'FEMALE': ('female', _('Female')),
    'UNKNOWN': ('unknown', _('Unknown')),
})

TG_MARRIAGE_STATUS = Enum({
    'SINGLE': ('single', _('Single')),
    'RELATIONSHIP': ('relationship', _('in a relationship')),
    'MARRIED': ('married', _('Married')),
})

TG_AGES = Enum({
    '0_10': ('0-10', _('0-10')),
    '10_20': ('10-20', _('10-20')),
    '20_30': ('20-30', _('20-30')),
    '30_40': ('30-40', _('30-40')),
    '40_50': ('40-50', _('40-50')),
    '50_60': ('50-60', _('50-60')),
    '60_+': ('60+', _('60+')),
})

TG_MSG_GROUPS = Enum({
    'PUSH_DIRECTLY': ('empty', _('push directly')),
    'SMART_DISTRIBUTION': ('smart', _('smart distribution')),
})

SEARCH_TREND = Enum({
    'GO_UP': (0, _('go up')),
    'NO_CHANGE': (1, _('no change')),
    'GO_DOWN': (2, _('go down')),
})

SUBJECT_TML = Enum({
    'NOT_SET': (0, _('not set')),
    'FIRST': (1, _('template 1')),
    'SECOND': (2, _('template 2')),
    'THIRD': (3, _('template 3')),
    # a speical template for tianyi zhuanqu
    'T101': (101, _('tainyi sepcial')),
})

GROUP_MAPPING = {
    u'四川省电信': 'sichuan',
}

APP_LABELS = [
    {
        'key': 'safe',
        'name': u'安全状态',
        'select_mode': 'single',
        'tags': [
            u'未知',
            u'风险',
            ['multiple', u'安全', [u'百度安全管家扫描通过', u'360手机卫士扫描通过', u'腾讯手机管家扫描通过', u'金山手机毒霸扫描通过', u'LBE安全大师扫描通过', u'安全管家扫描通过']],
        ],
    }, {
        'key': 'ad',
        'name': u'广告状态',
        'select_mode': 'single',
        'tags': [
            u'无广告',
            ['multiple', u'有广告', [u'内置广告', u'Notification弹窗广告']],
        ],
    }, {
        'key': 'others',
        'name': u'其他标签',
        'select_mode': 'multiple',
        'tags': [
            u'首发',
            u'官方',
            u'热门',
            u'精品',
            u'推荐',
            u'积分',
            u'V标',
            ['multiple', u'隐私', [u'访问通话记录、联系人数据', u'访问短信隐私数据', u'获取手机定位信息', u'读取手机识别码、型号等隐私', u'无隐私']],
        ],
    }
]
