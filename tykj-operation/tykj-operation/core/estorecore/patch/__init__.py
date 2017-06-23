import logging
import pymongo
import datetime
from django.conf import settings
from estorecore.servemodels.patch import PatchMongodbStorage

logger = logging.getLogger('estorecore')

remote_patch_db = PatchMongodbStorage(settings.P_MONGODB_CONF)
patch_db = PatchMongodbStorage(settings.MONGODB_CONF)


def check_p():
    # remote_patch_db._db.patch.ensure_index("update_dt")
    from_dt = datetime.datetime.utcnow()
    newest_patch = patch_db._db.patch.find_one(sort=[("update_dt", pymongo.DESCENDING)])
    if newest_patch:
        from_dt = newest_patch['update_dt']
    else:
        remote_patch = remote_patch_db._db.patch.find_one(sort=[("update_dt", pymongo.ASCENDING)])
        if remote_patch:
            from_dt = remote_patch['update_dt']
    patchs = [p for p in remote_patch_db._db.patch.find({'update_dt': {"$gt": from_dt}})]
    print 'NEW PATCHS %s' % len(patchs)
    for p in patchs:
        cond = {
                "old_hash": p["old_hash"],
                "new_hash": p["new_hash"],
            }
        data = {
                "old_hash": p["old_hash"],
                "new_hash": p["new_hash"],
                "download_url": p["download_url"],
                "new_size": p["new_size"],
                "patch_size": p["patch_size"],
                "update_dt": p["update_dt"],
            }
        patch_db._db.patch.update(cond, data, True)
