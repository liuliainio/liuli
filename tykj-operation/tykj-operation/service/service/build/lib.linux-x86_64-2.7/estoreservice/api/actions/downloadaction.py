# -*- coding: utf-8 -*-
from baseaction import BaseAction
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from estorecore.servemodels.app import APP_FIELDS_DOWNLOAD_WITH_PROMOTE
from estoreservice.api.actions.appupdateaction import AppUpdateAction
from estoreservice.openapi.errors import resource_not_exist
from estoreservice.utils.requestparameters import *
from estoreservice.utils.utils import build_apk_url
import os
import re
import urllib


class DownloadAction(BaseAction):

    def __init__(self, app_db, patch_db, logger):
        super(DownloadAction, self).__init__()
        self.app_db = app_db
        self.patch_db = patch_db
        self.logger = logger

    def reform_interception_url(self, url):
        can_remove_param_hosts = ['118.123.97.191', 'download.taobaocdn.com',
                                  'download.alipay.com', 'bs.baidu.com', 'cache.3g.cn',
                                  'gamecache.3g.cn', 'a4.img.3366.com', 'apps.wandoujia.com',
                                  '[0-9]+.[0-9]+.[0-9]+.[0-9]+/down.myapp.com']
        r = re.compile(
            '^http://(%s)/.*.apk\?.*$' %
            '|'.join(can_remove_param_hosts))
        if r.match(url):
            ret = url[0: url.find('.apk?') + 4]
            if self.logger:
                self.logger.info('reform url: %s to url: %s', url, ret)
            return ret
        else:
            return url

    def process_dolphin_download(self, request, parameters):
        #disabled download to default url
        disabled_seconds = 0
        if parameters[P_DISABLE_ME]:
            disabled_seconds = parameters[P_DISABLE_ME]

        if disabled_seconds > 0 or parameters[P_DOWNLOAD_URL].startswith(settings.CDN_APK_HOST):
            app = None
            download_url = parameters[P_DOWNLOAD_URL]
        else:
            download_url = self.reform_interception_url(parameters[P_DOWNLOAD_URL])
            app = self.app_db.get_app_by_external_download_url(download_url)

            if app:
                pmt = 0
                if 'promote' in app and app['promote'] > 0:
                    pmt = 1
                    response, _ = self._download_app(app, None, False, parameters[P_CHN])
                    response['app_name'] = urllib.quote(app['name'].encode('utf8') if isinstance(app['name'], unicode) else str(app['name']))
                    response['app_id'] = app['id']
                else:
                    response = HttpResponseRedirect(parameters[P_DOWNLOAD_URL])

                self.logger.info('dolphin_download with dolphin, chn=%s, clientid=%s, source=%s, download_url=%s, pageurl=%s, ip=%s, package=%s, id=%d, version=%d, pmt=%d'
                                 % (parameters[P_CHN],
                                     parameters[P_CLIENT_ID],
                                     parameters[P_SOURCE],
                                     download_url,
                                     parameters[P_PAGE_URL],
                                     parameters[P_IP],
                                     app['package_name'],
                                     app['id'],
                                     app['version_code'],
                                     pmt))

        if not app:
            self.logger.info('dolphin_download with external, chn=%s, clientid=%s, source=%s, download_url=%s, pageurl=%s, ip=%s, disabled=%d'
                             % (parameters[P_CHN], parameters[P_CLIENT_ID], parameters[P_SOURCE], download_url, parameters[P_PAGE_URL], parameters[P_IP], disabled_seconds))

            response = HttpResponseRedirect(download_url)

        if disabled_seconds > 0:
            response['dsec'] = disabled_seconds

        return response

    # app_id, source
    def process_download(self, request, parameters):
        has_patch = None
        if not AppUpdateAction.incremental_update_enabled(parameters[P_SOURCE]):
            parameters[P_OLD_HASH] = None

        app = None
        if parameters[P_APP_ID]:
            app = self.app_db.get_info(
                parameters[P_APP_ID],
                fields=APP_FIELDS_DOWNLOAD_WITH_PROMOTE)
        elif parameters[P_PACKAGE_NAME]:
            app = self.app_db.get_app_by_package(
                parameters[P_PACKAGE_NAME],
                platform=parameters[P_PLATFORM],
                jailbreak=parameters[P_JAILBREAK],
                fields=APP_FIELDS_DOWNLOAD_WITH_PROMOTE)

        if app:
            pmt = 0
            direct_download = app.get('manual', -1) < 0
            direct_download = False
            if 'promote' in app and app['promote'] > 0:
                pmt = 1
            elif direct_download:
                if 'external_download_urls' in app and app['external_download_urls']:
                    download_url = app['external_download_urls'][0]
                    self.logger.info('app_download_redicrect, chn=%s, clientid=%s, source=%s, ip=%s, package=%s, id=%s, external_url:%s'
                                     % (parameters[P_CHN],
                                        parameters[P_CLIENT_ID],
                                        parameters[P_SOURCE],
                                        parameters[P_IP],
                                        str(parameters[P_PACKAGE_NAME]),
                                        str(parameters[P_APP_ID]),
                                        download_url))
                    response = HttpResponseRedirect(download_url)
                else:
                    self.logger.info('app_download_404, chn=%s, clientid=%s, source=%s, ip=%s, package=%s, id=%s'
                                     % (parameters[P_CHN],
                                        parameters[P_CLIENT_ID],
                                        parameters[P_SOURCE],
                                        parameters[P_IP],
                                        str(parameters[P_PACKAGE_NAME]),
                                        str(parameters[P_APP_ID])))
                    response = resource_not_exist(request, str([parameters[P_APP_ID], parameters[P_PACKAGE_NAME]]))
                return response

            response, has_patch = self._download_app(
                app, parameters[P_OLD_HASH], parameters[P_IS_RENAME], parameters[P_CHN])
            self.logger.info('app_download, chn=%s, clientid=%s, source=%s, ip=%s, package=%s, id=%d, version=%d, haspatch=%d, pmt=%d'
                             % (parameters[P_CHN],
                                parameters[P_CLIENT_ID],
                                parameters[P_SOURCE],
                                parameters[P_IP],
                                app['package_name'],
                                app['id'],
                                app['version_code'],
                                1 if has_patch else 0,
                                pmt))
        else:
            self.logger.info('app_download_404, chn=%s, clientid=%s, source=%s, ip=%s, package=%s, id=%s'
                             % (parameters[P_CHN],
                                parameters[P_CLIENT_ID],
                                parameters[P_SOURCE],
                                parameters[P_IP],
                                str(parameters[P_PACKAGE_NAME]),
                                str(parameters[P_APP_ID])))
            response = resource_not_exist(request, str([parameters[P_APP_ID], parameters[P_PACKAGE_NAME]]))

        return response

    def _download_app(self, app, old_hash, is_rename, chn):
        app_id = app['id']
        package_name = app['package_name']

        if 'promote_apps' in app and chn in app['promote_apps']:
            promote_app = app['promote_apps'][chn]
            app.update(promote_app)
            is_rename = False

        patch_download_url, patch_hash = self._get_app_patch(app, old_hash)

        if patch_download_url:
            download_url = patch_download_url
            package_hash = patch_hash
            has_patch = True
        else:
            download_url = app['download_url']
            package_hash = app.get('package_hash', None)
            has_patch = False

        if not download_url.startswith('http://') and not download_url.startswith('https://'):
            download_url = self._build_final_download_url(
                download_url,
                package_name,
                app['version_code'],
                is_rename=is_rename,
                old_hash=old_hash)

        response = HttpResponseRedirect(download_url)
        if package_hash:
            response['package_hash'] = package_hash

        return (response, has_patch)

    def _get_app_patch(self, app, old_hash):
        new_hash = app.get('package_hash', None)
        if not old_hash or not new_hash:
            return (None, None)

        download_url = self.patch_db.get_patch_url(old_hash.lower(), new_hash)

        # TODO: return patch hash
        return (download_url, None)

    def _build_final_download_url(
            self, download_path, package_name, version_code, is_rename=True, old_hash=None):
        if is_rename and download_path.find('?') == -1:
            # Convert download path into user and CDN friendly path. For example,
            #     downloads/vol1/attachments/2010/05/4005_127358798077.apk
            # will be converted to:
            # downloads/vol1/<package_name>_<version_code>.apk?p=attachments/2010/05/4005_127358798077.apk
            ext = os.path.splitext(download_path)[1]
            if ext == ".patch":
                version_str = "%s_%s" % (version_code, old_hash)
            else:
                version_str = "%s" % version_code

            download_path = "%s%s_%s%s?p=%s" % (download_path[:download_path.find("/", len("downloads/")) + 1],
                                                package_name,
                                                version_str,
                                                ext,    # file suffix
                                                download_path[download_path.find("/", len("downloads/") + 1) + 1:])

        return build_apk_url(download_path)
