# -*- coding: utf-8 -*-
import os
import re
import md5
import logging
import zipfile
import mimetypes
from subprocess import Popen, PIPE
from os.path import dirname, realpath, join
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import FileSystemStorage
from django.utils.encoding import force_unicode

FIX_IMAGE_SIZE = 100*1024
COMPRESS_QUALITY = 75

SCRIPTS_PATH = join(dirname(dirname(dirname(realpath(__file__)))), 'scripts')
AAPT_PATH = join(SCRIPTS_PATH, 'aapt')
GET_SIGN_PATH = join(SCRIPTS_PATH, 'getSign.jar')
CMD_MD5 = 'md5sum "%s" | cut -d" " -f 1'
#kwinter@ubuntu:~$ md5sum EStore.apk  | cut -d" " -f 1
#f2bfcde30209ec0e0cf45e7b3e7ea1a3
CMD_PACKAGE_INFO = AAPT_PATH + ' dump badging "%s" | head -n 1'
#kwinter@ubuntu:~/workspace/TelecomEStore-Server/src/core/scripts$ ./aapt dump badging ~/EStore.apk | head -n 1
#package: name='com.eshore.ezone' versionCode='102' versionName='3.6.0.2'
PACKAGE_INFO_REGEX = re.compile(r"package: name='(.*)' versionCode='(.*)' versionName='(.*)'", re.I)
CMD_APP_INFO = AAPT_PATH + ' dump badging "%s" | grep application: '
#kwinter@ubuntu:~/workspace/TelecomEStore-Server/src/core/scripts$ ./aapt d badging ~/EStore.apk | grep application
#application: label=' 天翼空间' icon='res/drawable-hdpi/icon.png'
APP_INFO_REGEX = re.compile(r"application: label='(.+)' icon='(.+)'", re.I)
CMD_GET_SIGN = 'java -jar ' + GET_SIGN_PATH + ' "%s"'
#kwinter@ubuntu:~/workspace/TelecomEStore-Server/src/core/scripts$ java -jar getSign.jar ~/EStore.apk
#-127-63-97-128-48-7362930-75-511367-103-99-2-785227-2
CMD_UNZIP_FILE = 'unzip "%s" -d %s'

#sdkVersion:'6'
MIN_SDK_VERSION_INFO_REGEX = re.compile(r"sdkVersion:'(\d+)'", re.I)
CMD_MIN_SDK_VERSION_INFO = AAPT_PATH + ' dump badging "%s" | grep sdkVersion:'

logger = logging.getLogger('estorecore')


def _md5(string):
    m = md5.new()
    m.update(string)
    return m.hexdigest()


def get_package_name_from_temp_file(temp_file):
    package_name = None
    if type(temp_file) == str:
        file_path = temp_file
    else:
        file_path = temp_file.temporary_file_path()
    try:
        info = Popen(CMD_PACKAGE_INFO % file_path, stdout=PIPE, shell=True).communicate()[0].replace('\n', '')
        m = PACKAGE_INFO_REGEX.search(info)
        if m:
            package_name = m.group(1)
    except Exception, e:
        logger.exception('get package info failed, cmd: %s, error: %s' % (CMD_PACKAGE_INFO % file_path, e))
    return package_name


def extract_apk_info(obj, with_apk_sign=False, only_apk_sign=False):
    apk_info = {}
    file_path = obj.download_path.path
    if not only_apk_sign:
        apk_info['size'] = obj.download_path.size
        try:
            md5hash = Popen(CMD_MD5 % file_path, stdout=PIPE, shell=True).communicate()[0].replace('\n', '')
            apk_info['package_hash'] = md5hash
        except Exception, e:
            logger.exception('generate md5 failed, cmd: %s, error: %s' % (CMD_MD5 % file_path, e))
        try:
            info = Popen(CMD_PACKAGE_INFO % file_path, stdout=PIPE, shell=True).communicate()[0].replace('\n', '')
            m = PACKAGE_INFO_REGEX.search(info)
            if m:
                apk_info['package_name'] = m.group(1)
                apk_info['version_code'] = int(m.group(2) or 0)
                apk_info['version_name'] = force_unicode(m.group(3))
        except Exception, e:
            logger.exception('get package info failed, cmd: %s, error: %s' % (CMD_PACKAGE_INFO % file_path, e))
        try:
            min_sdk_info = Popen(CMD_MIN_SDK_VERSION_INFO % file_path, stdout=PIPE, shell=True).communicate()[0].replace('\n', '')
            m2 = MIN_SDK_VERSION_INFO_REGEX.search(min_sdk_info)
            if m2:
                apk_info['min_sdk_version'] = int(m2.group(1) or 0)
        except Exception, e:
            logger.exception('get min_sdk_version info failed, cmd: %s, error: %s' \
                    % (CMD_MIN_SDK_VERSION_INFO % file_path, e))
        try:
            info = Popen(CMD_APP_INFO % file_path, stdout=PIPE, shell=True).communicate()[0].replace('\n', '')
            m = APP_INFO_REGEX.search(info)
            if m:
                apk_info['name'] = m.group(1)
                icon_path = m.group(2)
                icon_content = None
                try:
                    apk_zipfile = zipfile.ZipFile(file_path)
                    if icon_path in apk_zipfile.namelist():
                        icon_content = apk_zipfile.read(icon_path)
                    apk_zipfile.close()
                except Exception, e:
                    logger.warn('extract apk with zipfile failed, error: %s' % e)
                    extract_dir = '/tmp/%s' % apk_info.get('package_hash', 'tmp_unpack_dir')
                    os.popen(CMD_UNZIP_FILE % (file_path, extract_dir))
                    icon_content = open(os.path.join(extract_dir, icon_path)).read()
                    os.popen('rm -rf %s' % extract_dir)
                if icon_content:
                    icon_name = '%s.%s' % (_md5(''.join([str(obj.id), apk_info.get('package_hash', ''), icon_path])), icon_path.split('.')[-1])
                    icon_file = SimpleUploadedFile(icon_name, icon_content, content_type=mimetypes.guess_type(icon_path))
                    apk_info['icon'] = (icon_name, icon_file)
            #obj.icon_path = int(infos[1].split('=')[1].replace("'",""))
        except Exception, e:
            logger.exception('get app info failed, cmd: %s, error: %s' % (CMD_APP_INFO % file_path, e))
    if (not only_apk_sign and with_apk_sign) or only_apk_sign:
        try:
            sign = Popen(CMD_GET_SIGN % file_path, stdout=PIPE, shell=True).communicate()[0].replace('\n', '')
            apk_info['package_sign'] = sign
        except Exception, e:
            logger.exception('get app sign failed, cmd: %s, error: %s' % (CMD_GET_SIGN % file_path, e))
    return apk_info

#@param abs_in_file_path : absolute file path
#@param rel_in_file_path : relative file path
def compress_image(abs_in_file_path, rel_in_file_path, quality=COMPRESS_QUALITY):
    new_ext = '.jpg'

    #prevent concurrency problem
    import random,time
    t = random.uniform(0.1,0.3)
    time.sleep(t)

    if abs_in_file_path:
        suffix = str(int(time.time()))
        abs_path_filename,ext = os.path.splitext(abs_in_file_path)
        abs_out_file_path = abs_path_filename + suffix + new_ext

        rel_path_filename,ext = os.path.splitext(rel_in_file_path)
        rel_out_file_path = rel_path_filename + suffix + new_ext

        #setting convert quality, default is 75%
        quality = quality if quality < 100 and quality > 10 else COMPRESS_QUALITY
        ret = os.system('convert -quality %d%% %s %s' % (quality, abs_in_file_path, abs_out_file_path))
        if ret == 0:
            os.remove(abs_in_file_path)
            return rel_out_file_path
    return rel_in_file_path

class LocalFileSystemStorage(FileSystemStorage):

    def __init__(self, location=None, base_url=None):
        if location is None:
            location = settings.UPLOAD_FILE_ROOT
        self.location = os.path.abspath(location)
        self.base_url = "http://%s" % settings.SITE_DOMAIN

    def save(self, name, content):
        file_path = super(LocalFileSystemStorage, self).save(name, content)
        if file_path.split('.')[-1].lower() in ('jpg', 'jpeg', 'png', 'gif') and self.exists(file_path) and self.size(file_path) > FIX_IMAGE_SIZE:
            return compress_image( self.path(file_path), file_path )
        return file_path
