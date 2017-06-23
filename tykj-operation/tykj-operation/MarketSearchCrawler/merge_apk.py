# coding=utf-8
import datetime
import MySQLdb
from hashlib import md5
from BeautifulSoup import BeautifulSoup
from services.db import MySQLdbWrapper


import sys
reload(sys)
getattr(sys, 'setdefaultencoding')('utf8')

_db = MySQLdbWrapper()


CATE_MAPS = {
    'wandoujia.com': {
        u'系统': '系统安全',
        u'安全': '系统安全',
        u'输入法': '输入浏览',
        u'浏览器': '输入浏览',
        u'通信': '聊天通讯',
        u'社交': '网络社区',
        u'影音': '影音阅读',
        u'阅读': '影音阅读',
        u'拍照': '摄影美化',
        u'美化': '摄影美化',
        u'资讯': '新闻资讯',
        u'地图': '出行导航',
        u'生活': '生活实用',
        u'健康': '生活实用',
        u'理财': '购物理财',
        u'词典': '学习办公',
        u'办公': '学习办公',
        u'休闲益智': '益智休闲',
        u'动作竞技': '动作格斗',
        u'体育竞速': '体育竞速',
        u'射击冒险': '飞行射击',
        u'模拟养成': '模拟养成',
        u'经营策略': '策略经营',
        u'角色扮演': '角色冒险',
    },
    'appchina.com': {
        u'系统工具': '系统安全',
        u'输入法': '输入浏览',
        u'浏览器': '输入浏览',
        u'通话通讯': '聊天通讯',
        u'社交网络': '网络社区',
        u'主题插件': '主题桌面',
        u'动态壁纸': '主题桌面',
        u'影音播放': '影音阅读',
        u'图书阅读': '影音阅读',
        u'拍摄美化': '摄影美化',
        u'新闻资讯': '新闻资讯',
        u'便捷生活': '生活实用',
        u'网购支付': '购物理财',
        u'金融理财': '购物理财',
        u'学习办公': '学习办公',
        u'益智': '益智休闲',
        u'益智游戏': '益智休闲',
        u'音乐游戏': '音乐其他',
        u'辅助工具': '音乐其他',
        u'手机网游': '网络游戏',
        u'动作冒险': '动作格斗',
        u'对战格斗': '动作格斗',
        u'体育运动': '体育竞速',
        u'赛车竞速': '体育竞速',
        u'射击': '飞行射击',
        u'射击游戏': '飞行射击',
        u'虚拟养成': '模拟养成',
        u'模拟经营': '策略经营',
        u'策略': '策略经营',
        u'策略游戏': '策略经营',
        u'棋牌桌游': '桌游棋牌',
        u'角色扮演': '角色冒险',
    },
    'zhushou.360.cn': {
        u'系统.输入': '系统安全',
        u'聊天.通讯': '聊天通讯',
        u'网络.邮件': '网络社区',
        u'壁纸.主题': '主题桌面',
        u'影音.图像': '影音阅读',
        u'阅读.学习': '影音阅读',
        u'生活.地图': '出行导航',
        u'办公.商务': '学习办公',
        u'休闲益智': '益智休闲',
        u'网络游戏': '网络游戏',
        u'动作冒险': '动作格斗',
        u'体育竞速': '体育竞速',
        u'飞行射击': '飞行射击',
        u'经营策略': '策略经营',
        u'棋牌天地': '桌游棋牌',
        u'角色扮演': '角色冒险',
    },
    'as.baidu.com': {
        u'系统安全': '系统安全',
        u'聊天通讯': '聊天通讯',
        u'网络社区': '网络社区',
        u'影音图像': '影音阅读',
        u'书籍阅读': '影音阅读',
        u'壁纸美化': '摄影美化',
        u'地图导航': '出行导航',
        u'生活实用': '生活实用',
        u'其他软件': '生活实用',
        u'理财购物': '购物理财',
        u'学习办公': '学习办公',
        u'休闲益智': '益智休闲',
        u'其他游戏': '益智休闲',
        u'动作格斗': '动作格斗',
        u'体育竞速': '体育竞速',
        u'飞行射击': '飞行射击',
        u'经营养成': '模拟养成',
        u'策略游戏': '策略经营',
        u'卡片棋牌': '桌游棋牌',
        u'角色冒险': '角色冒险 ',
    },
    'myapp.com': {
        u'社交': '聊天通讯',
        u'系统': '系统安全',
        u'安全': '系统安全',
        u'工具': '生活实用',
        u'通讯': '聊天通讯',
        u'音乐': '影音阅读',
        u'娱乐': '生活实用',
        u'美化': '主题桌面',
        u'视频': '影音阅读',
        u'阅读': '影音阅读',
        u'生活': '生活实用',
        u'导航': '出行导航',
        u'摄影': '摄影美化',
        u'教育': '学习办公',
        u'理财': '购物理财',
        u'健康': '生活实用',
        u'新闻': '新闻资讯',
        u'购物': '购物理财',
        u'办公': '学习办公',
        u'旅游': '出行导航',
        u'休闲': '益智休闲',
        u'赛车': '体育竞速',
        u'棋牌': '桌游棋牌',
        u'动作': '动作格斗',
        u'角色': '角色冒险',
        u'射击': '飞行射击',
        u'格斗': '动作格斗',
        u'冒险': '角色冒险',
        u'战略': '策略经营',
        u'体育': '体育竞速',
        u'网游': '网络游戏',
    },
}


def init_file(file):
    dic = {'id': file[0],
           'name': file[1],
           'icon_link': file[2],
           'icon_path': file[3],
           'source': file[4],
           'source_link': file[5],
           'rating': file[6],
           'version': file[7],
           'developer': file[8],
           'sdk_support': file[9],
           'category': file[10],
           'screen_support': file[11],
           'apk_size': file[12],
           'language': file[13],
           'publish_date': file[14],
           'downloads': file[15],
           'description': file[16],
           'images': file[17],
           'images_path': file[18],
           'qr_link': file[19],
           'download_link': file[20],
           'last_crawl': file[21],
           'vol_id': file[22],
           'package_name': file[23],
           'version_code': file[24],
           'sig': file[25],
           'min_sdk_version': file[26],
           'is_break': file[27],
           'platform': file[28],
           'file_type': file[29],
           'update_note': file[30],
           'package_hash': file[31],
           'labels': file[32],
           }
    try:
        if dic['source'] == 'nduoa.com':
            dic['downloads'] = dic['downloads'].replace(u',', '')
            dic['apk_size'] = get_apk_size(dic.get('apk_size'))
        elif dic['source'] == 'hiapk.com':
            dic['apk_size'] = get_apk_size(dic.get('apk_size'))
        elif dic['source'] == 'goapk.com':
            if dic.get('downloads') and u'\u5927\u5c0f\uff1a' in dic['downloads'].decode('utf8'):
                dic['apk_size'] = dic['downloads'].decode('utf8')
                dic['downloads'] = 0
            if dic.get('category') and u'\u5927\u5c0f\uff1a' in dic['category'].decode('utf8'):
                dic['apk_size'] = dic['category'].decode('utf8')
                dic['category'] = ''
            if dic.get('category') and u'\u7c7b\u522b' in dic['category'].decode('utf8'):
                dic['category'] = dic['category'].split(':')[1]
            dic['version'] = get_version(dic['version'])
            dic['apk_size'] = get_apk_size(dic.get('apk_size'))
        elif dic['source'] == 'appchina.com':
            dic['apk_size'] = get_apk_size(dic.get('apk_size'))
        elif dic['source'] == 'mumayi.com':
            if dic.get('apk_size') and u'\u672a\u77e5' in dic['apk_size'].decode('utf8'):
                dic['apk_size'] = 0
            dic['apk_size'] = get_apk_size(dic.get('apk_size'))
        elif dic['source'] == 'as.baidu.com':
            dic['developer'] = None
        if dic.get('description') and not dic['source'] != 'api.1mobile.com':
            soup = BeautifulSoup(dic.get('description').decode('utf8'))
            dic['description'] = soup.getText('\n')
        else:
            dic['desctiption'] = ''
        dic['rating'] = get_raing(dic.get('rating'))
        dic['category'] = _adapt_cate_str(dic['source'], dic.get('category'))
        dic['update_note'] = dic['update_note'] or ""
    except Exception as e:
        print '[%s]INITIAL FILE FAILED [%s],  %s' % (datetime.datetime.now(), dic['source_link'], e)
        import traceback
        print traceback.format_exc()
        return None
    return dic


def _adapt_cate_str(source, cate_str):
    if not cate_str:
        print'[WARNING] No category.'
        return u'生活实用'
    if not isinstance(cate_str, unicode):
        cate_str = cate_str.decode('utf-8')
    cate_str = cate_str.strip()
    if source == 'api.1mobile.com':
        return cate_str
    cate_str = CATE_MAPS[source].get(cate_str, u'生活实用')
    return cate_str


def get_raing(rating):
    if not rating:
        return 0
    rating = float(rating)
    if rating >= 10:
        rating = rating / 10
    else:
        rating = 0
    return rating


def get_version(version):
    try:
        version = version.decode('utf8')
        version = version.replace(u'\u7248\u672c\uff1a', '').strip()
    except Exception as e:
        print e
    return version


def get_apk_size(apk_size):
    if not apk_size:
        return 0
    apk_size = _adapt_colon_str(apk_size, 1)
    if ',' in apk_size:
        apk_size = apk_size.replace(',', '')
    if 'MB' in apk_size:
        apk_size = int(float(apk_size.replace('MB', '').strip()) * 1024 * 1024)
    elif 'KB' in apk_size:
        apk_size = int(float(apk_size.replace('KB', '').strip()) * 1024)
    elif 'M' in apk_size:
        apk_size = int(float(apk_size.replace('M', '').strip()) * 1024)
    elif 'K' in apk_size:
        apk_size = int(float(apk_size.replace('K', '').strip()) * 1024)
    return apk_size


def _adapt_colon_str(str, index):
    if u'\uff1a' in str:
        return str.split(u'\uff1a')[index].strip()
    elif ':' in str:
        return str.split(':')[index].strip()
    else:
        return str


def merge():
    print '[%s]START MERGE APK.' % datetime.datetime.now()
    files = get_apk(50)
    if not files:
        update_final_app_version()
        return
    result_list = []
    report_list = []
    for file in files:
        apk = init_file(file)
        result = check_file(apk)
        if not result:
            report_list.append((file[0], 2))
            continue
        result_list.append(result)
        report_list.append((file[0], 1))
    insert_apk(result_list)
    report_status(report_list)


def update_final_app_version():
    try:
        cursor = _db.cursor()
        sql = '''
        insert ignore into
            final_app_version (id,package_name,version_code)
        select a.id,b.package_name,b.version_code
        from final_app a
            join(select package_name ,MAX(version_code ) as version_code
                from final_app Group by package_name)b
            on a.package_name=b.package_name and a.version_code=b.version_code
        '''
        cursor.execute(sql)
        _db.conn.commit()
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()


def check_file(file):
    if not file or not file['package_name'] or not file['sig'] or not file['package_hash']:
        return None
#        file['package_name'],file['version_code'],file['version'] = get_package_info(file['app_path'])
#        if not file['package_name']:
#            return None
    return file


def get_apk(num):
    try:
        cursor = _db.cursor()
        sql = """
        SELECT unique_apk.id,name,icon_link,icon_path,app.source,app.source_link,rating,
            app.version,developer,sdk_support,category, app.screen_support,unique_apk.apk_size,language,
            publish_date,downloads,description,images,images_path,qr_link,unique_apk.download_link,
            last_crawl,vol_id,package_name,version_code,sig,min_sdk_version,is_break,platform,
            file_type, update_note, package_hash, labels
        FROM app,unique_apk
        WHERE app.source_link = unique_apk.source_link
            and unique_apk.tag2 is null
            and unique_apk.img_status=11 limit %d
        """ % num
        cursor.execute(sql)
        result = cursor.fetchall()
        return result
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()


def insert_apk(list):
    for file in list:
        try:
            cursor = _db.cursor()
            file_path = get_path(file['download_link'], 'apk')
            sql = """
            INSERT IGNORE INTO final_app
                (name,icon_link,icon_path,source,source_link,rating,version,developer,
                sdk_support,category,screen_support,apk_size,language,publish_date,downloads,
                description,images,images_path,qr_link,download_link,last_crawl,package_name,
                version_code,file_path,vol_id, sig, min_sdk_version, is_break, platform, file_type,
                update_note, package_hash, avail_download_links, labels, created_at)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now())
            """
            cursor.execute(sql, (file['name'], file['icon_link'], file['icon_path'], file['source'],
                                 file['source_link'], file['rating'], file['version'], file['developer'],
                                 file['sdk_support'], file['category'], file['screen_support'], file['apk_size'],
                                 file['language'], file['publish_date'], file['downloads'], file['description'],
                                 file['images'], file['images_path'], file['qr_link'], file['download_link'],
                                 file['last_crawl'], file['package_name'], file['version_code'], file_path,
                                 file['vol_id'], file['sig'], file['min_sdk_version'], file['is_break'],
                                 file['platform'], file['file_type'], file['update_note'], file['package_hash'],
                                 file['download_link'], file['labels']))
            _db.conn.commit()
        except MySQLdb.Error as e:
            print e
        finally:
            cursor.close()
        print '[%s]INSERT APK [%s]%s(%s,%s)' % \
            (datetime.datetime.now(), file['source'], file['name'], file['package_name'], file['version'])


def report_status(list):
    for l in list:
        try:
            cursor = _db.cursor()
            sql = "UPDATE unique_apk SET tag2 = %s WHERE id = %s"
            cursor.execute(sql, (l[1], l[0]))
            _db.conn.commit()
        except MySQLdb.Error as e:
            print e
        finally:
            cursor.close()


def get_path(link, suffix):
    file_name = '%s.%s' % (md5(link).hexdigest().upper(), suffix)
    dir1 = file_name[:2]
    dir2 = file_name[2:4]
    path = "%s/%s/%s" % (dir1, dir2, file_name)
    return path


if __name__ == "__main__":
    merge()





