import os, re, hashlib
import datetime
import time
import daemon
from estorecore.models.app import AppVersion,Application
from estorecore.models.update import UpdateApp
from estorecore.servemodels.patch import PatchMongodbStorage
from estorecore.servemodels.app import AppMongodbStorage
from estoreoperation import settings
import logging
import rpc
from apkpatch_gen.ttypes import ApkPatchStatus
from multiprocessing import Pool

_PATCH_DB = PatchMongodbStorage(settings.MONGODB_CONF)
logger = logging.getLogger("scripts")

def _get_thrift_connection(conf):
    server_dicts = []
    servers = conf.split(',')
    for server in servers:
        parts = server.split(':')
        server_dicts.append({
                'host': parts[0],
                'port': parts[1],
            })
    return rpc.ApkPatchService(server_dicts)

_service = _get_thrift_connection(settings.PATCH_SERVICE_HOST)


class PatchDaemon(daemon.Daemon):

    def run(self):
        gen_patch_worker()

def _get_new_appversion(vcode, avs):
    new_av = None
    for av in avs:
        if av.version_code == int(vcode):
            new_av = av
            break
    return new_av

def queue_patch_job(pid, vcode, phash=None):
    HASH_LENGTH = 32
    if pid:
        avs = AppVersion.objects.filter(app__id=pid, version_code__lte=vcode).order_by('-version_code')[:4]
        if avs:
            new_hash = phash
            if not new_hash:
                new_av = _get_new_appversion(vcode,avs)
                if not new_av:
                    info_msg = 'NO NEW APPVERSION IN MYSQL DB PACKAGE NAME(%s,%s)' % (pid,vcode)
                    logger.info(info_msg)
                    return
                new_hash = new_av.package_hash

            for old_av in avs:
                old_hash = old_av.package_hash

                if not old_hash:
                    continue

                if old_av.version_code == int(vcode):
                    continue
                if len(old_hash) < HASH_LENGTH or len(new_hash) < HASH_LENGTH:
                    info_msg ='HASH LENGTH LESS THAN 32:%s, %s, %s' % (old_av.id, old_hash, new_hash)
                    logger.info(info_msg)
                    continue

                if _PATCH_DB.get_patch_url(old_hash, new_hash):
                    info_msg = 'PATCH EXISTS %s, %s' % (old_hash, new_hash)
                    logger.info(info_msg)
                    continue

                _PATCH_DB.add_job(old_hash, new_hash)
                info_msg = '[%s]ADD JOB OLD_HASH:%s, NEW_HASH:%s' % (datetime.datetime.now(), old_hash, new_hash)
                logger.info(info_msg)
            else:
                info_msg = 'APPVERSION NO HASH VERSION(%s)' % pid
                logger.info(info_msg)
        else:
            info_msg = 'NO APPVERSION IN MYSQL DB PACKAGE NAME(%s,%s)' % (pid,vcode)
            logger.info(info_msg)
    else:
        info_msg = 'NO APPLICATION IN MYSQL DB PACKAGE NAME(%s)' % pid
        logger.info(info_msg)


def queue_single_patch_job(pname, vcode, phash=None):
    apps = Application.objects.filter(package_name=pname)
    if apps:
        info_msg = 'PATCH APPLICATION IN MYSQL DB PACKAGE NAME(%s)' % pname
        logger.info(info_msg)
        app = apps[0]
        queue_patch_job(app.id, vcode, phash)
    else:
        info_msg = 'NO PATCH APPLICATION IN MYSQL DB PACKAGE NAME(%s)' % pname
        logger.info(info_msg)


def queue_log_patch_job(app_id_list):
    _APP_DB = AppMongodbStorage(settings.MONGODB_CONF)
    if app_id_list:
        for app_id in app_id_list:
            try:
                app = _APP_DB._db.apps.find_one({'id':app_id},fields=["package_name", "package_hash", "id", "version_code"])
                if app:
                    vcode = app.get('version_code')
                    phash = app.get('package_hash')
                    info_msg = 'MONGODB APP INFO:id:%s, vcode:%s, phash:%s' % (app_id, vcode, phash)
                    queue_patch_job(app_id, vcode, phash)
                else:
                    info_msg = 'MONGODB APP INFO: App(%s) is not in mongodb' % app_id
            except Exception,e:
                print e
                info_msg = str(e)
            finally:
                logger.info(info_msg)
    _APP_DB._conn.close()


def gen_patch(old_hash, new_hash):
    try:
        old_file = hash2localpath(old_hash)
        new_file = hash2localpath(new_hash)
    except Exception, e:
        print e
        return
    if not (old_file and new_file):
        return

    result = _service.bsdiff(old_hash, new_hash, old_file, new_file)
    if not result:
        print 'THRIFT API FAILED. result:%s' % result
    if result.status == ApkPatchStatus.SUCCEED:
        print "patch %s(%s) %s(%s) %s(%s) %s" % (old_file, result.old_size, new_file, result.new_size, result.patch_file, result.patch_size, result.patch_hash)
        download_url = localpath2url(result.patch_file)
        _PATCH_DB.upsert(old_hash, new_hash, download_url, result.new_size, result.patch_size, result.patch_hash)
    else:
        print "patch failed %s %s %s" % (old_file, new_file, result.patch_file)

def gen_patch_worker():
    pool = Pool(processes=4)
    while True:
        try:
            job = _PATCH_DB.fetch_job()
            old_hash = job['old_hash']
            new_hash = job['new_hash']
            print "[%s]RECEIVED JOB: %s - %s" % (datetime.datetime.now(), old_hash, new_hash)
            ret = pool.apply_async(gen_patch, (old_hash, new_hash))
            time.sleep(2)
            #gen_patch(old_hash, new_hash)
        except Exception, e:
            print e

def localpath2url(path):
    '''
    /mnt/ctappstore2/vol1/xx/xx/xxxx => downloads/vol1/xx/xx/xxx
    /mnt/ctappstore2/static/apks/xxx => static/apks/xxx
    '''
    m = re.match(r"%s/[^/]+/(vol\d+/.+)" % settings.MNT_ROOT, path)
    if m:
        return "downloads/" + m.group(1)
    m = re.match(r"%s/(.+)" % settings.STATIC_ROOT, path)
    if m:
        return "static/" + m.group(1)


def hash2localpath(package_hash):
    package_hash = package_hash.strip()
    for appver in AppVersion.objects.filter(package_hash=package_hash)[:1]:
        path = url2localpath(appver.download_path.name)
        return path
    print "Can't find local file for hash: %s" % package_hash
    return None


def url2localpath(download_url):
    '''
    downloads/vol1/xx/xx/xxx => /mnt/ctappstore2/vol1/xx/xx/xxxx
    static/apks/xxx => /mnt/ctappstore2/static/apks/xxx
    '''
    match = re.match("downloads/(.+)", download_url)
    if match:
        download_url = match.group(1)
    else:
        match = re.match("static/(.+)", download_url)
        if match:
            match_content = match.group(1)
            if match_content.startswith('iapks'):
                file_path = match_content.replace('iapks','')
                file_path = file_path.strip('/')
                return os.path.join('/mnt/ctappstore2/static/apks/',file_path)
            else:
                path = os.path.join('/mnt/ctappstore2', match.group(0))
                return path
    return find_absolute_path(download_url)

APK_VOL_MAPPING = {
        'vol3': '/mnt/ctappstore1',
        'vol4': '/mnt/ctappstore1',
        'vol5': '/mnt/ctappstore1',
        'vol11': '/mnt/ctappstore1',
        'vol12': '/mnt/ctappstore1',

        'vol1': '/mnt/ctappstore2',
        'vol6': '/mnt/ctappstore2',
        'vol7': '/mnt/ctappstore2',
        'vol8': '/mnt/ctappstore2',
        'vol10': '/mnt/ctappstore2',

        'vol9': '/mnt/ctappstore3',
        'vol13': '/mnt/ctappstore3',
        'vol14': '/mnt/ctappstore3',

        'vol2': '/mnt/ctappstore4',
        'vol15': '/mnt/ctappstore4',
        'vol16': '/mnt/ctappstore4',
        'vol17': '/mnt/ctappstore4',

        'vol18': '/mnt/ctappstore5',
        'vol19': '/mnt/ctappstore5',

        'vol155': '/mnt/ctappstore100',
        'vol156': '/mnt/ctappstore100',
        'vol157': '/mnt/ctappstore100',
        'vol158': '/mnt/ctappstore100',
        'vol159': '/mnt/ctappstore100',
        'vol161': '/mnt/ctappstore100',
        'vol162': '/mnt/ctappstore100',
        'vol163': '/mnt/ctappstore100',
        'vol164': '/mnt/ctappstore100',
        'vol107': '/mnt/ctappstore100',

        'vol343': '/mnt/ctappstore300',
        'vol344': '/mnt/ctappstore300',
        'vol345': '/mnt/ctappstore300',
        'vol346': '/mnt/ctappstore300',
        'vol349': '/mnt/ctappstore300',
        'vol350': '/mnt/ctappstore300',
        'vol351': '/mnt/ctappstore300',
        'vol352': '/mnt/ctappstore300',
        'vol353': '/mnt/ctappstore300',
        'vol354': '/mnt/ctappstore300',
        'vol20': '/mnt/ctappstore6',
        'vol21': '/mnt/ctappstore6',
        'vol22': '/mnt/ctappstore6',
        'vol23': '/mnt/ctappstore6',
        'vol24': '/mnt/ctappstore6',
        'vol25': '/mnt/ctappstore6',
        'vol26': '/mnt/ctappstore6',
        'vol27': '/mnt/ctappstore7',
        'vol28': '/mnt/ctappstore8',
    }


def find_absolute_path(path):
    '''
    path = "volx/xx/xx/xxxx" => abs_path = "/MNT_ROOT/???/volx/xx/xx/xxxx"
    '''
    vol = path.split('/')[0]
    if vol in APK_VOL_MAPPING:
        abs_path = os.path.join(APK_VOL_MAPPING[vol], path)
        return abs_path
    else:
        raise Exception("Can't find local path for %s" % path)



def file_md5(path):
    with open(path) as fp:
        data = fp.read()
    return hashlib.md5(data).hexdigest()


def ensure_dir(path):
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)


def file_size(path):
    stat = os.stat(path)
    return stat.st_size
