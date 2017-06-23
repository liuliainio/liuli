#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import os
import sys
import shutil
import datetime
import simplejson
from subprocess import Popen, PIPE

ROOT_DIR = '/mnt/data/ftphome/scan_apks'
DATE_FORMAT = '%Y%m%d'

AUTH_KEY = '9ORmsDOAJ3zcD21w'
API_URL = 'https://api.scan.qq.com/browser/scan'
API_RTN_INFO_REGEX = re.compile(r"{.*}", re.I)
DOWNLOAD_ROOT_URL = 'http://estoreops.189store.com/scan_apks'


def _call_scan_api(api_url, api_key, apk_download_url):
    cmd = 'curl -k -d \'{"authkey":"%s", "url":"%s"}\' %s' % (api_key, apk_download_url, api_url)
    print 'cmd: %s' % cmd
    info = Popen(cmd, stdout=PIPE, shell=True).communicate()[0].replace('\n', '')
    m = API_RTN_INFO_REGEX.search(info)
    if m:
        return m.group(0)
    return ''


def _format_scan_result(file_name, api_result):
    successed = False

    if not api_result:
        txt_info = u'%s:未知' % file_name
    else:
        api_res_dict = simplejson.loads(api_result)
        safe_type = api_res_dict.get('safetype', 'unknown')
        if safe_type == 'safe':
            txt_info = u'%s:安全' % file_name
            successed = True
        elif safe_type == 'virus':
            txt_info = u'%s:风险应用, 病毒名称: %s, 描述: %s' % (file_name, api_res_dict['virusname'], api_res_dict['virusdesc'])
            successed = True
        else:
            txt_info = u'%s:未知' % file_name
    return txt_info.encode('utf-8'), successed


def scan_apk(date_str, file_name):
    # call tx apk scan api
    file_path = os.path.join(ROOT_DIR, date_str, file_name)
    apk_download_url = file_path.replace(ROOT_DIR, DOWNLOAD_ROOT_URL)
    api_result = _call_scan_api(API_URL, AUTH_KEY, apk_download_url)
    # format api return info
    txt_info, status = _format_scan_result(file_name, api_result)
    print 'txt_info: %s, status: %s' % (txt_info, status)
    if status:
        txt_file = open(os.path.join(ROOT_DIR, date_str, 'results.txt'), 'a')
        txt_file.write(txt_info + '\n')
        # remove file to successed dir
        successed_scan_apk_dir = os.path.join(ROOT_DIR, date_str, 'successed_scan_apks')
        if not os.path.isdir(successed_scan_apk_dir):
            os.mkdir(successed_scan_apk_dir)
        shutil.move(file_path, os.path.join(successed_scan_apk_dir, file_name))


def walk_dir(root_dir, date_str):
    root_dir = os.path.join(root_dir, date_str)
    if not os.path.isdir(root_dir):
        os.mkdir(root_dir)
    for name in os.listdir(root_dir):
        if os.path.isfile(os.path.join(root_dir, name)):
            print 'file_name: %s' % name
            scan_apk(date_str, name)


if __name__ == "__main__":
    date_str = sys.argv[1] if len(sys.argv) >= 2 and len(sys.argv[1]) == 8 \
            else datetime.datetime.strftime(datetime.datetime.now(), DATE_FORMAT)
    walk_dir(ROOT_DIR, date_str)
