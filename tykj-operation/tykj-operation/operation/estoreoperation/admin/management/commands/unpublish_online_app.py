#coding:utf-8
from django.core.management.base import BaseCommand
from estoreoperation.app.models import Application
from estorecore.datasync.sync_app import sync_obj
from estorecore.servemodels.app import AppMongodbStorage
from django.conf import settings
import os
import pickle
import json

app_db = AppMongodbStorage(settings.MONGODB_CONF)


def is_app_online(app_id):
    app = app_db.get_info(app_id)
    return bool(app)


def make_id_set(id_list):
    id_set = set()
    for d_id in id_list:
        id_set.add(d_id)
    return id_set


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
    except Exception, e:
        print 'error: %s' % e
    finally:
        return data


def find_apps(index, count):
    end_index = index + count
    apps = Application.objects.filter(hided=0)[index: end_index]
    return apps


def unpublish_app(index, count, id_list):
    apps = find_apps(index, count)
    id_set = make_id_set(id_list)
    for app in apps:
        if app.id in id_set:
            continue
        else:
            print 'unpublished: ', app.id, app.name
            app.published = 0
            online_status = is_app_online(app.id)
            if online_status:
                sync_obj(app, Application)
            else:
                app.save()


class Command(BaseCommand):

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
            unpublish_app(start_index, count, id_list)

        else:
            print 'app id files does not exists!'
