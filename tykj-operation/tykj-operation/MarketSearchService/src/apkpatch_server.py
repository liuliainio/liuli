'''
Created on Match 18, 2013

@author: kunli
'''
import os
import sys
import datetime
import subprocess
from subprocess import Popen, PIPE
from MarketSearch.apkpatch_gen import ApkPatch
from MarketSearch.apkpatch_gen.ttypes import ApkPatchStatus, ApkPatchResult
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer


def ensure_dir(path):
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

def file_size(path):
    stat = os.stat(path)
    return stat.st_size

def bsdiff(oldfile, newfile, patchfile):
    subprocess.check_call('bsdiff "%s" "%s" %s' % (oldfile, newfile, patchfile), shell = True)

def filehash(filepath):
    cmd_md5 = 'md5sum "%s" | cut -d " " -f 1'
    md5hash = Popen(cmd_md5 % filepath, stdout=PIPE, shell=True).communicate()[0].replace('\n', '')
    if not len(md5hash) == 32:
        raise Exception('md5hash length is not 32, md5hash: %s' % md5hash)
    return md5hash

class ApkPatchHandler(ApkPatch.Iface):

    DEFAULT_PORT = 8666

    PATCH_ROOT = '/mnt/ctappstore7/vol28'

    def bsdiff(self, old_hash, new_hash, old_file, new_file):
        name = new_hash + "_" + old_hash + ".patch"
        print '[%s]processing %s' % (datetime.datetime.now(), name)
        patch_file = os.path.join(self.PATCH_ROOT, name[0:2], name[2:4], name)
        try:
            ensure_dir(patch_file)
            if not os.path.exists(patch_file):
                bsdiff(old_file, new_file, patch_file)
            old_size = file_size(old_file)
            new_size = file_size(new_file)
            patch_size = file_size(patch_file)
            result = ApkPatchResult(old_size=old_size, new_size=new_size, patch_size=patch_size, patch_file=patch_file, status=ApkPatchStatus.SUCCEED,
                    patch_hash=filehash(patch_file))
        except Exception, e:
            print 'bsdiff error:%s' % e
            result = ApkPatchResult(old_size=0, new_size=0, patch_size=0, patch_file=patch_file, status=ApkPatchStatus.FAIL, 
                    patch_hash='')
        sys.stdout.flush()
        return result


handler = ApkPatchHandler()
processor = ApkPatch.Processor(handler)
transport = TSocket.TServerSocket(host="0.0.0.0", port=ApkPatchHandler.DEFAULT_PORT)
tfactory = TTransport.TBufferedTransportFactory()
pfactory = TBinaryProtocol.TBinaryProtocolFactory()

server = TServer.TThreadedServer(processor, transport, tfactory, pfactory)

print "Starting apk patch server..."
server.serve()

