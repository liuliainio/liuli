from estorecore.db import MongodbStorage
from datetime import datetime
import time

class PatchMongodbStorage(MongodbStorage):

    db_name = "patch"

    def __init__(self,conn_str):
        super(PatchMongodbStorage, self).__init__(conn_str, self.db_name)
        # self._db.patch.ensure_index([("new_hash", 1), ("old_hash", 1)], unique = True)
        # self._db.job.ensure_index([("new_hash", 1), ("old_hash", 1)], unique = True)

    def get_patch_url(self, old_hash, new_hash):
        cond = {'old_hash' : old_hash, 'new_hash' : new_hash}
        data = self._db.patch.find_one(cond)
        return data['download_url'] if data else None

    def get_patch_info(self, old_hash, new_hash):
        cond = {'old_hash' : old_hash, 'new_hash' : new_hash}
        data = self._db.patch.find_one(cond)
        return  data

    def upsert(self, old_hash, new_hash, download_url, new_size, patch_size, patch_hash):
        cond = {
                 "old_hash" : old_hash,
                 "new_hash" : new_hash,
                }
        data = {
                "old_hash" : old_hash,
                "new_hash" : new_hash,
                "download_url": download_url,
                "new_size" : new_size,
                "patch_size" : patch_size,
                "patch_hash" : patch_hash,
                "update_dt" : datetime.utcnow(),
                }
        self._db.patch.update(cond, data, True)

    def add_job(self, old_hash, new_hash):
        cond = {
                "old_hash" : old_hash,
                "new_hash" : new_hash,
                }
        data = {
                "old_hash" : old_hash,
                "new_hash" : new_hash,
                "update_dt" : datetime.utcnow(),
                }
        self._db.job.update(cond, data, True)

    def fetch_job(self, block = True):
        job = None
        while True:
            job = self._db.job.find_and_modify({}, limit = 1, remove = True)
            if job or (not block):
                return job
            time.sleep(10)

