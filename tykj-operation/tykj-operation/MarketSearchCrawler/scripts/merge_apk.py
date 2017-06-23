# coding=utf-8
import time
import datetime
import sys
import os
import MySQLdb
from hashlib import md5
from BeautifulSoup import BeautifulSoup

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.db import MySQLdbWrapper


_db = MySQLdbWrapper()

cate_map_dic = {"442": "系统安全",
                "435": "系统安全",
                "441": "系统安全",
                "手机安全": "系统安全",
                "系统工具": "系统安全",
                "安全杀毒": "系统安全",
                "系统安全": "系统安全",
                "安全": "系统安全",
                "系统": "系统安全",
                "系统.输入": "系统安全",
                "主题桌面": "主题桌面",
                "11556": "主题桌面",
                "311": "主题桌面",
                "407": "主题桌面",
                "408": "主题桌面",
                "409": "主题桌面",
                "410": "主题桌面",
                "453": "主题桌面",
                "454": "主题桌面",
                "455": "主题桌面",
                "456": "主题桌面",
                "457": "主题桌面",
                "458": "主题桌面",
                "459": "主题桌面",
                "460": "主题桌面",
                "461": "主题桌面",
                "462": "主题桌面",
                "463": "主题桌面",
                "464": "主题桌面",
                "465": "主题桌面",
                "466": "主题桌面",
                "467": "主题桌面",
                "468": "主题桌面",
                "469": "主题桌面",
                "470": "主题桌面",
                "471": "主题桌面",
                "472": "主题桌面",
                "473": "主题桌面",
                "474": "主题桌面",
                "壁纸.主题": "主题桌面",
                "主题桌面": "主题桌面",
                "美化.壁纸": "主题桌面",
                "壁纸主题铃声": "主题桌面",
                "主题插件": "主题桌面",
                "动态壁纸": "主题桌面",
                "主题壁纸": "主题桌面",
                "聊天通讯": "聊天通讯",
                "438": "聊天通讯",
                "479": "聊天通讯",
                "通信聊天": "聊天通讯",
                "通讯.聊天": "聊天通讯",
                "通讯": "聊天通讯",
                "通信": "聊天通讯",
                "社交通讯": "聊天通讯",
                "通话通讯": "聊天通讯",
                "通话增强": "聊天通讯",
                "即时通讯": "聊天通讯",
                "短信增强": "聊天通讯",
                "聊天.通讯": "聊天通讯",
                "生活实用": "生活实用",
                "0": "生活实用",
                "494": "生活实用",
                "404": "生活实用",
                "405": "生活实用",
                "406": "生活实用",
                "442": "生活实用",
                "445": "生活实用",
                "447": "生活实用",
                "449": "生活实用",
                "450": "生活实用",
                "451": "生活实用",
                "452": "生活实用",
                "411": "生活实用",
                "412": "生活实用",
                "413": "生活实用",
                "437": "生活实用",
                "443": "生活实用",
                "480": "生活实用",
                "481": "生活实用",
                "482": "生活实用",
                "483": "生活实用",
                "484": "生活实用",
                "485": "生活实用",
                "486": "生活实用",
                "综合服务": "生活实用",
                "创意休闲": "生活实用",
                "其他": "生活实用",
                "其它": "生活实用",
                "生活": "生活实用",
                "健康": "生活实用",
                "DIY作品": "生活实用",
                "必备软件": "生活实用",
                "便捷生活": "生活实用",
                "辅助工具": "生活实用",
                "休闲娱乐": "生活实用",
                "其他软件": "生活实用",
                "影音阅读": "影音阅读",
                "436": "影音阅读",
                "544": "影音阅读",
                "545": "影音阅读",
                "10035": "影音阅读",
                "10036": "影音阅读",
                "10037": "影音阅读",
                "530": "影音阅读",
                "531": "影音阅读",
                "495": "影音阅读",
                "125": "影音阅读",
                "478": "影音阅读",
                "544": "影音阅读",
                "电子图书": "影音阅读_阅读",
                "音乐音频": "影音阅读",
                "影音图像": "影音阅读",
                "影音": "影音阅读",
                "视频播放": "影音阅读",
                "影音.图像": "影音阅读",
                "阅读.图书": "影音阅读_阅读",
                "阅读": "影音阅读_阅读",
                "阅读.学习": "影音阅读_阅读",
                "漫画电子书": "影音阅读_阅读",
                "小说.漫画": "影音阅读_阅读",
                "影音播放": "影音阅读",
                "图书阅读": "影音阅读_阅读",
                "音乐视频": "影音阅读",
                "图书动漫": "影音阅读_阅读",
                "书籍阅读": "影音阅读_阅读",
                "444": "学习办公",
                "办公学习": "学习办公",
                "办公.财经": "学习办公",
                "资讯.词典": "学习办公",
                "办公": "学习办公",
                "词典": "学习办公",
                "办公理财": "学习办公",
                "学习办公": "学习办公",
                "教育学习": "学习办公",
                "商务办公": "学习办公",
                "医疗保健": "学习办公",
                "办公.商务": "学习办公",
                "网络社区": "网络社区",
                "437": "网络社区",
                "440": "网络社区",
                "475": "网络社区",
                "476": "网络社区",
                "477": "网络社区",
                "497": "网络社区",
                "498": "网络社区",
                "499": "网络社区",
                "社交网络": "网络社区",
                "社交": "网络社区",
                "网络.社区": "网络社区",
                "社交网络": "网络社区",
                "社交微博": "网络社区",
                "网络.邮件": "网络社区",
                "社区.交友": "网络社区",
                "出行导航": "出行导航",
                "445": "出行导航",
                "489": "出行导航",
                "490": "出行导航",
                "气象交通": "出行导航",
                "旅行.地图": "出行导航",
                "地图导航": "出行导航",
                "天气时间": "出行导航",
                "出行地图": "出行导航",
                "地图": "出行导航",
                "生活.地图": "出行导航",
                "金融.理财": "购物理财",
                "购物理财": "购物理财",
                "理财购物": "购物理财",
                "理财": "购物理财",
                "446": "购物理财",
                "448": "购物理财",
                "487": "购物理财",
                "488": "购物理财",
                "493": "购物理财",
                "金融理财": "购物理财",
                "购物支付": "购物理财",
                "生活.购物": "购物理财",
                "生活购物旅行": "购物理财",
                "网购支付": "购物理财",
                "购物理财": "购物理财",
                "输入浏览": "输入浏览",
                "434": "输入浏览",
                "输入法": "输入浏览",
                "输入法.系统工具": "输入浏览",
                "输入法": "输入浏览",
                "网络浏览": "输入浏览_浏览器",
                "浏览器": "输入浏览_浏览器",
                "439": "摄影美化",
                "摄影美化": "摄影美化",
                "影音拍摄": "摄影美化",
                "拍摄美化": "摄影美化",
                "美化": "摄影美化",
                "拍照": "摄影美化",
                "摄影图像": "摄影美化",
                "壁纸美化": "摄影美化",
                "443": "新闻资讯",
                "新闻阅读": "新闻资讯",
                "新闻资讯": "新闻资讯",
                "资讯": "新闻资讯",
                "信息.资讯": "新闻资讯",
                "窗口小部件": "窗口小部件",
                "14346": "窗口小部件",
                "431": "益智休闲",
                "432": "益智休闲",
                "492": "益智休闲",
                "益智休闲": "益智休闲",
                "必备游戏": "益智休闲",
                "益智": "益智休闲",
                "其他游戏": "益智休闲",
                "休闲益智": "益智休闲",
                "角色冒险": "角色冒险",
                "420": "角色冒险",
                "421": "角色冒险",
                "422": "角色冒险",
                "角色扮演": "角色冒险",
                "冒险闯关": "角色冒险",
                "动作格斗": "动作格斗",
                "423": "动作格斗",
                "425": "动作格斗",
                "426": "动作格斗",
                "427": "动作格斗",
                "动作射击": "动作格斗",
                "动作竞技": "动作格斗",
                "动作冒险": "动作格斗",
                "格斗对战": "动作格斗",
                "街机模拟": "动作格斗",
                "对战格斗": "动作格斗",
                "动作游戏": "动作格斗",
                "433": "策略经营",
                "419": "策略经营",
                "策略经营": "策略经营",
                "策略塔防": "策略经营",
                "经营策略": "策略经营",
                "模拟经营": "策略经营",
                "策略游戏": "策略经营",
                "策略": "策略经营",
                "经营策略": "策略经营",
                "428": "体育竞速",
                "429": "体育竞速",
                "体育竞速": "体育竞速",
                "体育竞技": "体育竞速",
                "赛车竞速": "体育竞速",
                "体育运动": "体育竞速",
                "赛车游戏": "体育竞速",
                "424": "飞行射击",
                "竞技飞行": "飞行射击",
                "射击飞行": "飞行射击",
                "射击冒险": "飞行射击",
                "飞行射击": "飞行射击",
                "射击": "飞行射击",
                "桌游棋牌": "桌游棋牌",
                "430": "桌游棋牌",
                "557": "桌游棋牌",
                "558": "桌游棋牌",
                "益智棋牌": "桌游棋牌",
                "棋牌休闲": "桌游棋牌",
                "棋牌桌游": "桌游棋牌",
                "策略棋牌": "桌游棋牌",
                "卡片棋牌": "桌游棋牌",
                "棋牌天地": "桌游棋牌",
                "模拟养成": "模拟养成",
                "421": "模拟养成",
                "模拟游戏": "模拟养成",
                "经营养成": "模拟养成",
                "虚拟养成": "模拟养成",
                "养成经营": "模拟养成",
                "网络模拟": "网络游戏",
                "网络游戏": "网络游戏",
                "手机网游": "网络游戏",
                "音乐其他": "音乐其他",
                "559": "音乐其他",
                "音乐游戏": "音乐其他",
                "书籍": "书籍",
                "532": "书籍",
                "533": "书籍",
                "534": "书籍",
                "535": "书籍",
                "536": "书籍",
                "537": "书籍",
                "538": "书籍",
                "539": "书籍",
                "540": "书籍",
                "541": "书籍",
                "542": "书籍",
                "543": "书籍",
                "491": "书籍",
                "546": "漫画",
                "漫画": "漫画",
                "547": "漫画",
                "548": "漫画",
                "549": "漫画",
                "550": "漫画",
                "551": "漫画",
                "552": "漫画",
                "553": "漫画",
                "554": "漫画",
                "555": "漫画",
                "556": "漫画",
                "有声阅读": "有声阅读",
                "12095": "有声阅读",
                "12096": "有声阅读",
                "资料": "资料",
                "笑话": "笑话",
                "14376": "资料",
                "10992": "笑话",
                "音乐": "音乐",
                "414": "音乐",
                "511": "音乐",
                "496": "音乐",
                "500": "音乐",
                "501": "音乐",
                "502": "音乐",
                "503": "音乐",
                "504": "音乐",
                "505": "音乐",
                "506": "音乐",
                "507": "音乐",
                "508": "音乐",
                "509": "音乐",
                "510": "音乐",
                "511": "音乐",
                "视频": "视频",
                "512": "视频",
                "513": "视频",
                "514": "视频",
                "515": "视频",
                "516": "视频",
                "517": "视频",
                "518": "视频",
                "519": "视频",
                "520": "视频",
                "521": "视频",
                "522": "视频",
                "523": "视频",
                "524": "视频",
                "525": "视频",
                "526": "视频",
                "527": "视频",
                "528": "视频",
                "529": "视频",
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
           'package_hash': file[30],
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
        if dic.get('description'):
            soup = BeautifulSoup(dic.get('description').decode('utf8'))
            dic['description'] = soup.getText('\n')
        else:
            dic['desctiption'] = ''
        dic['rating'] = get_raing(dic.get('rating'))
        dic['category'] = _adapt_cate_str(dic.get('category'))
    except Exception as e:
        print dic['source_link']
        print e
    return dic


def _adapt_cate_str(cate_str):
    if not cate_str:
        return '生活实用'
    cate_str = cate_str.strip()
    cate_str = cate_map_dic[cate_str]
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
    while True:
        files = get_apk(100)
        if not files:
            print '[%s] no new files.' % datetime.datetime.now()
            return
        result_list = []
        report_list = []
        for file in files:
            file = init_file(file)
            result = check_file(file)
            if not result:
                report_list.append((file['id'], 2))
                continue
            result_list.append(result)
            report_list.append((file['id'], 1))
        insert_apk(result_list)
        report_status(report_list)


def update_final_app_version():
    try:
        cursor = _db.cursor()
        sql = 'insert ignore into final_app_version (id,package_name,version_code) select a.id,b.package_name,b.version_code from final_app a join(select package_name ,MAX(version_code ) as version_code from final_app Group by package_name)b on a.package_name=b.package_name and a.version_code=b.version_code'
        cursor.execute(sql)
        _db.conn.commit()
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()


def check_file(file):
    if not file['package_name'] or not file['sig']:
        return None
#        file['package_name'],file['version_code'],file['version'] = get_package_info(file['app_path'])
#       if not file['package_name']:
 #          return None
    return file


def get_apk(num):
    try:
        cursor = _db.cursor()
        sql = "SELECT unique_apk.id,name,icon_link,icon_path,app.source,app.source_link,rating, app.version,developer,sdk_support,category, app.screen_support,unique_apk.apk_size,language,publish_date,downloads,description,images,images_path,qr_link,unique_apk.download_link,last_crawl,vol_id,package_name,version_code,sig,min_sdk_version,is_break,platform,file_type,package_hash FROM app,unique_apk WHERE app.source_link = unique_apk.source_link and unique_apk.tag2 is null and unique_apk.img_status=11 limit %d" % num
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
            sql = "INSERT IGNORE INTO final_app (name,icon_link,icon_path,source,source_link,rating,version,developer,sdk_support,category,screen_support,apk_size,language,publish_date,downloads,description,images,images_path,qr_link,download_link,last_crawl,package_name,version_code,file_path,vol_id, sig, min_sdk_version, is_break, platform, file_type, package_hash) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(
                sql,
                (file['name'],
                 file['icon_link'],
                    file['icon_path'],
                    file['source'],
                    file['source_link'],
                    file['rating'],
                    file['version'],
                    file['developer'],
                    file['sdk_support'],
                    file['category'],
                    file['screen_support'],
                    file['apk_size'],
                    file['language'],
                    file['publish_date'],
                    file['downloads'],
                    file['description'],
                    file['images'],
                    file['images_path'],
                    file['qr_link'],
                    file['download_link'],
                    file['last_crawl'],
                    file['package_name'],
                    file['version_code'],
                    file_path,
                    file['vol_id'],
                    file['sig'],
                    file['min_sdk_version'],
                    file['is_break'],
                    file['platform'],
                    file['file_type'],
                    file['package_hash']))
            _db.conn.commit()
            print '[%s] insert new apk. (%s,%s)' % (datetime.datetime.now(), file['package_name'], file['version'])
        except MySQLdb.Error as e:
            print e
        finally:
            cursor.close()


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
