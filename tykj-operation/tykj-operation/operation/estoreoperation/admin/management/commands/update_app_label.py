#coding:utf-8
from django.core.management.base import BaseCommand
from estoreoperation.app.models import Application
from estorecore.datasync.sync_app import sync_obj
from estorecore.servemodels.app import AppMongodbStorage
from django.conf import settings
import os
import pickle
import json

TMP_FILE = '/tmp/pickle.tmp'

app_db = AppMongodbStorage(settings.MONGODB_CONF)
full_label = u'{"safe":{"name":"安全状态","tag":[],"sub_tag":{}},"ad":{"name":"广告状态","tag":[],"sub_tag":{}},"others":{"name":"其他标签","tag":["官方"],"sub_tag":{}}}'
#encdoing for mysql save pure str
full_label_encoded = full_label.encode('utf-8')
official_word = u'官方'


def is_app_online(app_id):
    app = app_db.get_info(app_id)
    return bool(app)

def make_tid_set(id_list):
    tid_set = set()
    for t_id in id_list:
        tid_set.add(t_id)
    return tid_set

def save_temp(data):
    with open(TMP_FILE, 'wb') as f:
        pickle.dump(data, f)

def read_temp():
    data = []
    try:
        if not os.path.exists(TMP_FILE):
            return data
        with open(TMP_FILE, 'rb') as f:
            data = pickle.load(f)
        os.remove(TMP_FILE)
    except Exception,e:
        print 'error: %s' % e
    finally:
        return data


def find_by_id(id_set):
    apps = []
    if id_set:
        apps = Application.objects.filter(id__in=id_set)
    return apps


def find_by_tid(tid_set, start_index, count=1000):
    end_index = start_index + count
    #find app by t_id
    apps = [ app for app in Application.objects.all()[start_index:end_index] if app.t_id not in tid_set]
    return apps


def label_apps(apps):
    error_id_set = set()
    current_app_id = None

    try:
        for i,app in enumerate(apps):
            print '\nlocation:%s' % i
            label_dict = {}
            current_app_id = app.id
            if app.hided == 1:
                continue
            #update msyql
            if app.label:
                label_str = app.label
                label_dict = json.loads(label_str)
                if official_word not in label_dict['others']['tag']:
                    label_dict['others']['tag'].append(official_word)
                    print '[update tag]'
                app.label = json.dumps(label_dict, ensure_ascii=False).encode('utf-8')
            else:
                print '[add tag]'
                app.label = full_label_encoded

            #update online
            if is_app_online(app.id):
                #update mysql status again
                app.published = 1
                app.sync_status = 1
                sync_obj(app, Application)
                print 'update online: %s' % app.id
            else:
                print '%s not in online' % app.id
            app.save()
            print 'save app: %s' % app.id
    except Exception,e:
        print 'Fail to Sync:%s, %s' % (current_app_id, e)
        if current_app_id:
            error_id_set.add(current_app_id)
    finally:
        save_temp(error_id_set)




class Command(BaseCommand):
    '''
    File_Type: times script
    Function: find app and update its label then syncto mongodb
    '''
    help = ('update mysql and mongodb app label'
            '--id_path: file path'
            )

    def handle(self, id_path, start_index, count, **kwargs):
        start_index = int(start_index)
        count = int(count)

        if id_path and os.path.isfile(id_path):
            id_list = []
            fp = open(id_path, 'r')
            for app_id in fp:
                app_id = app_id.strip()
                if app_id and app_id.isdigit():
                    try:
                        id_list.append(int(app_id))
                    except:
                        print 'Can not convert app_id:%s' % app_id
            fp.close()
            print 'app counts:%s' % len(id_list)
            tid_set = make_tid_set(id_list)
            apps = find_by_tid(tid_set, start_index, count)
            fail_id_list = read_temp()
            fail_apps = find_by_id(fail_id_list)
            apps.extend(fail_apps)
            label_apps(apps)
        else:
            print 'app id files does not exists!'

