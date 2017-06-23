# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from estorecore.models.region import PhoneRegion
from estorecore.datasync.sync_app import sync_obj
from estoreoperation.region.xpinyin import Pinyin
import os

p = Pinyin()

#file-format: phone,province,city
def check_file_completed(file_path):
    if file_path and os.path.isfile(file_path):
        fp = open(file_path, 'r')
        for line in fp:
            try:
                line = line.strip()
                if line:
                    line_list = line.split(',')
                    if len(line_list) != 3:
                        continue
                    phone_num,province,city = line_list
                    if len(phone_num) < 7:
                        continue
                    phone_num = int(phone_num)
                    region = PhoneRegion.objects.filter(phone=phone_num)
                    if region:
                        continue
                    else:
                        city = city.decode('utf-8')
                        province = province.decode('utf-8')
                        city_pinyin = p.get_pinyin(city)
                        province_pinyin = p.get_pinyin(province)
                        r = PhoneRegion(city=city,city_pinyin=city_pinyin,province=province,province_pinyin=province_pinyin,phone=phone_num,published=1)
                        r.save()
                        print city,city_pinyin,province,province_pinyin,phone_num
            except Exception,e:
                print e,line
    else:
        print 'phone region file is not exists.'

def sync_region_to_mongo():
    all_phone = PhoneRegion.objects.filter(published=1,sync_status=0)
    try:
        for item in all_phone:
            sync_obj(item, PhoneRegion)
            print item.phone, item.province
    except Exception,e:
        print e


class Command(BaseCommand):

    def help(self):
        print 'usage:python manage.py sync_phone_region update file_path or sync'

    def handle(self, *args, **kwargs):
        param_length = len(args)
        if param_length == 0:
            self.help()
        elif param_length == 1:
            action = args[0]
            if action == 'sync':
                sync_region_to_mongo()
                print 'sync'
            else:
                self.help()
        elif param_length > 1:
            action = args[0]
            file_path = args[1]
            if action == 'update':
                print file_path
                check_file_completed(file_path)
            else:
                self.help()
