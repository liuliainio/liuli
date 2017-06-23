# -*- coding: utf-8 -*-
import os
import urllib
import estoreservice.utils.requestparameters as R
from baseaction import BaseAction
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from estorecore.servemodels.app import APP_FIELDS_DOWNLOAD_WITH_PROMOTE
from estoreservice.api.actions.appupdateaction import AppUpdateAction
from estoreservice.openapi.errors import resource_not_exist
from estoreservice.utils.utils import build_apk_url


class UpdateServiceAction(BaseAction):

    def __init__(self, app_db, patch_db, logger):
        super(DownloadAction, self).__init__()
        self.app_db = app_db
        self.patch_db = patch_db
        self.logger = logger

    def execute(self, request, parameters):
        client_id = get_parameter_GET(request, 'clientid')
        chn = get_parameter_GET(request, 'chn')
        pn = get_parameter_GET(request, 'pn')
        src = get_parameter_GET(request, 'src')
        vn = get_parameter_GET(request, 'vn', convert_func=int)
        auto = get_parameter_GET(request, 'auto', required=False)
        did = get_parameter_GET(request, 'did', required=False)
        os = get_parameter_GET(request, 'os', required=False)
        osvn = get_parameter_GET(request, 'osvn', required=False)
        re = get_parameter_GET(request, 're', required=False)
        # does not process currently
        cpu = get_parameter_GET(request, 'cpu', required=False)
        md = get_parameter_GET(request, 'md', required=False)
        rom = get_parameter_GET(request, 'rom', required=False)
        old_hash = get_parameter_GET(request, 'old_hash', required=False)
        #partner = get_parameter_GET(request, 'partner', required=False, default=u'xianxia')
        #broker = get_parameter_GET(request, 'broker', required=False, default=u'')

        for q in (chn, pn, src, vn):
            if isinstance(q, HttpResponse):    # convert failed
                return q
        result = update_db.get_update(
            pn, src, vn, is_auto=auto, device_id=did, os=os,
            os_version=osvn, resolution=re, cpu=cpu, device_model=md, rom=rom, client_id=client_id, chn=chn, old_hash=old_hash)
        if result is not None:
            if 'download_link' in result:
                result['download_url'] = result['download_link']
            if 'download_url' in result:
                result['download_url'] = combine_url(
                    settings.APK_HOST,
                    result['download_url'])

        logger.info(
            'update_service, chn=%s, client_id=%s, result=%s' %
            (chn, client_id, result))
        return result

    def process_download(self, request, parameters):
        if not AppUpdateAction.incremental_update_enabled(parameters[R.P_SOURCE]):
            parameters[R.P_OLD_HASH] = None

        app = None
        if parameters[R.P_APP_ID]:
            app = self.app_db.get_info(
                parameters[R.P_APP_ID],
                fields=APP_FIELDS_DOWNLOAD_WITH_PROMOTE)
        elif parameters[R.P_PACKAGE_NAME]:
            app = self.app_db.get_app_by_package(
                parameters[R.P_PACKAGE_NAME],
                platform=parameters[R.P_PLATFORM],
                jailbreak=parameters[R.P_JAILBREAK],
                fields=APP_FIELDS_DOWNLOAD_WITH_PROMOTE)

        if app:
            response, has_patch = self._download_app(
                app, parameters[R.P_OLD_HASH], parameters[R.P_IS_RENAME], parameters[R.P_CHN])
            self.logger.info('app_download, chn=%s, clientid=%s, source=%s, ip=%s, package=%s, id=%d, version=%d, haspatch=%d'
                             % (parameters[R.P_CHN], parameters[R.P_CLIENT_ID], parameters[R.P_SOURCE], parameters[R.P_IP], app['package_name'], app['id'], app['version_code'], 1 if has_patch else 0))
        else:
            self.logger.info('app_download_404, chn=%s, clientid=%s, source=%s, ip=%s, package=%s, id=%s'
                             % (parameters[R.P_CHN], parameters[R.P_CLIENT_ID], parameters[R.P_SOURCE], parameters[R.P_IP], str(parameters[R.P_PACKAGE_NAME]), str(parameters[R.P_APP_ID])))
            response = resource_not_exist(
                request, str([parameters[R.P_APP_ID], parameters[R.P_PACKAGE_NAME]]))

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
