# coding=utf-8
import requests
import MySQLdb
import time
from BeautifulSoup import BeautifulSoup
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.db import MySQLdbWrapper

_db = MySQLdbWrapper()


cate_page_pool = {"https://itunes.apple.com/cn/genre/ios-you-xi-dong-zuo-you-xi/id7001?mt=8": 0}

cate_map = {'7001': "动作游戏",
            '7002': "探险游戏",
            '7003': "街机游戏",
            '7004': "桌面游戏",
            '7005': "扑克牌游戏",
            '7006': "娱乐场游戏",
            '7007': "骰子游戏",
            '7008': "教育游戏",
            '7009': "家庭游戏",
            '7010': "儿童游戏",
            '7011': "音乐游戏",
            '7012': "智力游戏",
            '7013': "赛车游戏",
            '7014': "角色扮演游戏",
            '7015': "模拟游戏",
            '7016': "体育游戏",
            '7017': "策略游戏",
            '7018': "小游戏",
            '7019': "文字游戏",
            }


def start_crawler():
    while True:
        try:
            page = get_cate_page()
            if not page:
                print 'finished!'
                return
            cate_page_pool[page] = 1
            data = requests.get(page).content
            soup = BeautifulSoup(data)
            links = soup.findAll('a')
            cate_id = page.split('/id')[1].split('?mt')[0]
            analyzing_links(cate_id, links)
            print page
            time.sleep(3)
        except Exception as e:
            print e
            file = open('itunes_game_cate.txt', 'a')
            file.write(page)
            file.close()


def get_cate_page():
    for page in cate_page_pool.keys():
        if cate_page_pool[page] == 0:
            return page


def analyzing_links(cate_id, links):
    for link in links:
        href = link.get('href')
        text = link.text
        onclick = link.get('onclick')
        if href.startswith('https://itunes.apple.com/cn/genre/') and 'id700' in href and not onclick:
            if href not in cate_page_pool:
                cate_page_pool[href] = 0
        elif href.startswith('https://itunes.apple.com/cn/app/'):
            app_id = href.split('/id')[1].split('?mt')[0]
            app_name = text
            insert_db(app_id, app_name, cate_id, cate_map[cate_id])


def insert_db(app_id, app_name, cate_id, cate_name):
    try:
        cursor = _db.cursor()
        sql = "insert ignore into itunes_game_cate (app_id,app_name,cate_id,cate_name) values (%s, %s, %s, %s)"
        cursor.execute(sql, (app_id, app_name, cate_id, cate_name))
        _db.conn.commit()
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()


if __name__ == "__main__":
    start_crawler()
