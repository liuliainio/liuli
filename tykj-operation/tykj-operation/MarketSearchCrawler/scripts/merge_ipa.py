# coding=utf-8
import os
import MySQLdb
import random
from hashlib import md5
from BeautifulSoup import BeautifulSoup
import hashlib
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.db import MySQLdbWrapper

_db = MySQLdbWrapper()

cate_map_dic = {"工具": "系统管理",
                "效率": "系统管理",
                "社交一": "即时聊天",
                "社交二": "社区交友",
                "主题美化": "主题美化",
                "娱乐": "视频软件",
                "摄影与录像": "图像处理",
                "音乐": "书籍杂志",
                "图书": "书籍杂志",
                "新闻": "新闻阅读",
                "报刊杂志": "书籍杂志",
                "导航": "地图导航",
                "天气": "查询参考",
                "旅行": "查询参考",
                "其他工具": "生活购物",
                "生活": "生活健康",
                "医疗": "生活健康",
                "体育": "生活健康",
                "美食佳饮": "生活健康",
                "健康健美": "生活健康",
                "文档处理": "生活购物",
                "财务": "理财工具",
                "商品指南": "理财工具",
                "商业": "名片管理",
                "参考": "电子词典",
                "教育": "儿童教学",
                "游戏": "休闲娱乐",
                "街机游戏": "休闲娱乐",
                "桌面游戏": "棋牌天地",
                "智力游戏": "益智游戏",
                "扑克牌游戏": "棋牌天地",
                "小游戏": "休闲娱乐",
                "娱乐场游戏": "休闲娱乐",
                "音乐游戏": "休闲娱乐",
                "家庭游戏": "休闲娱乐",
                "儿童游戏": "休闲娱乐",
                "文字游戏": "益智游戏",
                "骰子游戏": "棋牌天地",
                "教育游戏": "益智游戏",
                "网络游戏": "网络游戏",
                "射击游戏": "射击游戏",
                "动作游戏": "动作游戏",
                "赛车游戏": "竞速游戏",
                "体育游戏": "体育竞技",
                "模拟游戏": "模拟经营",
                "策略游戏": "策略游戏",
                "探险游戏": "冒险游戏",
                "角色扮演游戏": "角色扮演",
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
        if dic.get('description'):
            soup = BeautifulSoup(dic.get('description').decode('utf8'))
            dic['description'] = soup.getText('\n')
        else:
            dic['desctiption'] = ''
        if dic['source'] == 'itunes.apple.com':
            if '游戏' in dic['sig']:
                if '网游' in dic['name'] or 'online' in dic['name']:
                    dic['category'] = '网络游戏'
                elif '飞机' in dic['name'] or '射击' in dic['name']or '飞行' in dic['name']:
                    dic['category'] = '射击游戏'
                else:
                    dic['category'] = dic['sig']
            else:
                if '主题' in dic['name'] or '壁纸' in dic['name']:
                    dic['category'] = '主题美化'
                elif dic['category'] == '社交':
                    dic['category'] = random.choice(['社交一', '社交二'])
            dic['category'] = _adapt_cate_str(dic.get('category'))
    except Exception as e:
        print dic['source_link']
        print e
    return dic


def _adapt_cate_str(cate_str):
    if not cate_str:
        return '系统管理'
    cate_str = cate_str.strip()
    cate_str = cate_map_dic[cate_str]
    return cate_str


def merge():
    while True:
        files = get_apk(100)
        if not files:
            update_final_app_version()
            return
        result_list = []
        report_list = []
        for file in files:
            file = init_file(file)
            result_list.append(file)
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


def get_apk(num):
    try:
        cursor = _db.cursor()
        sql = "SELECT unique_apk.id,name,icon_link,icon_path,app_ios.source,app_ios.source_link,rating, unique_apk.version,developer,sdk_support,category, app_ios.screen_support,unique_apk.apk_size,language,publish_date,downloads,description,images,images_path,qr_link,unique_apk.download_link,last_crawl,vol_id,package_name,version_code,sig,min_sdk_version,is_break,platform,file_type,package_hash FROM app_ios,unique_apk WHERE app_ios.source_link = unique_apk.source_link and unique_apk.tag2 is null and unique_apk.img_status=11 limit %d" % num
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
            file_path = get_path(file['download_link'], 'ipa')
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


def _get_icon_path(icon_link):
    image_guid = hashlib.sha1(icon_link).hexdigest()
    return 'full/%s/%s/%s.jpg' % (image_guid[:1], image_guid[1:3], image_guid)


def _get_images_path(images):
    images_path = []
    for image in images.split():
        image_guid = hashlib.sha1(image).hexdigest()
        image_path = 'full2/%s/%s/%s.jpg' % (image_guid[:1], image_guid[1:3], image_guid)
        images_path.append(image_path)
    return ' '.join(images_path)


if __name__ == "__main__":
    merge()
