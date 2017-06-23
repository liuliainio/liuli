# -*- coding: utf-8 -*-
import time
from django.http import HttpResponse

from baseaction import BaseAction
from estorecore.db import timestamp_utc_now
from estorecore.utils import friendly_size
from estoreservice.api.utils import get_parameter_GET, get_parameter_POST, get_parameter_META, get_parameter_POST_or_GET
from estoreservice.utils.utils import app_post_process, to_int_array

UA_PACKAGE_NAME = 0
UA_VERSION_CODE = 1
UA_PACKAGE_HASH = 2


class AppUpdateAction(BaseAction):

    @staticmethod
    def incremental_update_enabled(source):
        if not source:
            return True

        try:
            s = source.rsplit('_', 1)
            client_version = int(s[1])
            client_name = s[0]
            if (client_name == 'com.diandian.appstore' and client_version < 333) or (client_name == 'com.eshore.ezone.whole' and client_version < 5020):
                return False
        except:
            pass

        return True

    def __init__(
            self, app_db, user_db, patch_db, logger, app_upload_logger):
        super(AppUpdateAction, self).__init__()
        self.app_db = app_db
        self.user_db = user_db
        self.patch_db = patch_db
        self.logger = logger
        self.app_upload_logger = app_upload_logger

    def _now_ms(self):
        return long(time.time() * 1000)

    def _parse_app_infos(self, app_infos, source, chn):
        app_infos = [app.rsplit(':') for app in app_infos.split('|')]
        for app in app_infos:
            app[UA_VERSION_CODE] = int(app[UA_VERSION_CODE])

        if source.startswith('com.diandian.appstore_') and chn != 'ofw':
            app_infos = [
                app for app in app_infos if app[
                    UA_PACKAGE_NAME] != 'com.diandian.appstore']

        return app_infos

    def process_incremental_update(self, results, app_infos):
        package_hash_dict = dict([(app[UA_PACKAGE_NAME], app[UA_PACKAGE_HASH])
                                 for app in app_infos if len(app) > UA_PACKAGE_HASH])
        for result in results:
            result['patch_size'] = 0

            old_hash = package_hash_dict.get(result['package_name'], None)
            if not old_hash:
                continue
            old_hash = old_hash.lower()

            new_hash = result.get('package_hash', None)
            if not new_hash:
                continue

            patch_info = self.patch_db.get_patch_info(old_hash, new_hash)
            if not patch_info:
                # On demand calculate patch
                # self.patch_db.add_job(old_hash, new_hash)
                continue

            result['patch_size'] = friendly_size(patch_info['patch_size'])
            del result['package_hash']

    def query_app_updates(self, app_infos, category_id, platform, jailbreak):
        # TODO: support app type
        # if jailbreak is not None:
        #     results = app_db.query_updates(app_infos, platform = platform, jailbreak = jailbreak)
        # else:
        #     results = app_db.query_updates([app for app in app_infos if app['appType'] == 0], platform = platform, jailbreak = jailbreak)
        #     results += app_db.query_updates([app for app in app_infos if app['appType'] != 0], platform = platform, jailbreak = jailbreak)

        return (
            self.app_db.query_updates(
                [app[0] for app in app_infos],
                platform=platform,
                jailbreak=jailbreak,
                category_id=category_id)
        )

    def execute(self, request):
        time_start = self._now_ms()
        chn = get_parameter_POST_or_GET(
            request,
            'chn',
            required=False,
            str_max_length=255)
        client_id = get_parameter_POST_or_GET(request, 'clientid')
        source = get_parameter_POST_or_GET(
            request,
            'source',
            str_max_length=255)
        app_infos_str = get_parameter_POST_or_GET(
            request,
            'appinfos',
            str_max_length=2 *
            1024 *
            1024)
        # 0: upload only, return empty array, 1: return apps with new versions,
        # 2: return all known apps
        retlevel = get_parameter_POST_or_GET(
            request,
            'retlevel',
            required=False,
            convert_func=int,
            default=2)
        device_model = get_parameter_POST_or_GET(
            request,
            'device_model',
            required=False,
            str_max_length=255)
        os_v = get_parameter_POST_or_GET(
            request,
            'os',
            required=False,
            convert_func=int,
            default=0)
        screen_size = get_parameter_POST_or_GET(
            request,
            'screensize',
            required=False,
            str_max_length=255)
        platform = get_parameter_POST_or_GET(
            request,
            'platform',
            convert_func=to_int_array,
            default='1')
        jailbreak = get_parameter_POST_or_GET(
            request,
            'jailbreak',
            convert_func=int,
            default=0)
        category_id = get_parameter_POST_or_GET(
            request,
            'category_id',
            required=False,
            convert_func=int,
            default=0)
        # format: empty, dolphin
        format = get_parameter_POST_or_GET(
            request,
            'format',
            required=False,
            str_max_length=255)
        ip = get_parameter_META(
            request,
            'REMOTE_ADDR',
            required=False,
            default=u'')
        for q in (client_id, source, app_infos_str, retlevel, device_model, os_v, screen_size):
            if isinstance(q, HttpResponse):
                self.logger.warn(
                    'app_updates2, ip=%s, clientid=%s, param=%s, invalid request' %
                    (ip, client_id, str(q)))
                return q

        if jailbreak == -1:
            # this is used for pc client, for which, there's no jailbreak
            # concept, and it requires the app to keep the jailbreak status
            jailbreak = None
        elif jailbreak == 1:
            jailbreak = True
        else:
            jailbreak = False
        if len(platform) == 1:
            platform = platform[0]

        results = []
        has_new_version_apps = []
        if retlevel > 0:
            app_infos = self._parse_app_infos(app_infos_str, source, chn)

            results = self.query_app_updates(
                app_infos,
                category_id,
                platform,
                jailbreak)

            user_app_versions = dict(
                [(app[UA_PACKAGE_NAME], app[UA_VERSION_CODE]) for app in app_infos])
            has_new_version_apps = [app for app in results if int(
                app['version_code']) > user_app_versions.get(app['package_name'],
                                                             0)]
            if retlevel == 1:
                results = has_new_version_apps

            if AppUpdateAction.incremental_update_enabled(source):
                self.process_incremental_update(results, app_infos)

            results = app_post_process(
                results,
                os=os_v,
                screen_size=screen_size)

        self.app_upload_logger.info('ip=%s, clientid=%s, source=%s, device_model=%s, retlevel=%d, os=%s, screensize=%s, category_id=%d, appinfos=%s, newversions=%s, timetaken=%d'
                                    % (ip, client_id, source, device_model, retlevel, os_v, screen_size, category_id, app_infos_str, '|'.join([str(app['id']) for app in has_new_version_apps]), self._now_ms() - time_start))

        if format == 'dolphin':
            results = {
                'apps': results,
                'display_type': -1,
                'icon_url': '',
                'display_message': '',
                'page_url': ''}

        return results
