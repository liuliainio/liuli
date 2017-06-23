#coding:utf-8
from django.core.management.base import BaseCommand
from estoreoperation.patch.service import queue_log_patch_job, _PATCH_DB
from django.conf import settings
import os

class Command(BaseCommand):
    '''
    File_Type: cronb script
    Function: find app ids and patch apks from api log analyzed
    '''
    help = ('queue app pathc jobs'
            '--id_path: file path'
            )

    def handle(self, id_path, **options):
        if id_path and os.path.isfile(id_path):
            id_list = []
            fp = open(id_path, 'r')
            for app_id in fp:
                app_id = app_id.strip()
                if app_id and app_id.isdigit():
                    id_list.append(int(app_id))
            fp.close()
            print 'app patch counts:%s' % len(id_list)
            queue_log_patch_job(id_list)
        else:
            print 'patch id files does not exists!'
        _PATCH_DB._conn.close()

