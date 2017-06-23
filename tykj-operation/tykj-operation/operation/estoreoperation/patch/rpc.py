
import logging
from estoreoperation.utils import ThriftConnection, retry, remote_rpc
from apkpatch_gen import ApkPatch

logger = logging.getLogger("estoreoperation")

class ApkPatchService(ThriftConnection):


    def __init__(self, servers, client_cls=ApkPatch.Client, timeout=600000, keepalive=False):
        super(ApkPatchService, self).__init__(servers, client_cls, timeout=timeout, keepalive=keepalive)

    @remote_rpc(logger, swallow_error=True)
    @retry
    def bsdiff(self, old_hash, new_hash, old_file, new_file):
        return self.client.bsdiff(old_hash, new_hash, old_file, new_file)

