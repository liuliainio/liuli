from estorecore.db import MongodbStorage, IncrementalId, \
        cursor_to_list, timestamp_utc_now

class UploadMongodbStorage(MongodbStorage):

    db_name = "upload"

    def __init__(self, conn_str):
        super(UploadMongodbStorage, self).__init__(conn_str, self.db_name)
        self._ids = IncrementalId(self._db)

    def count_crash(self, date, count=1):
        self._db.crashstats.update({'date': date}, {'$inc': {'count': count}}, True)

    def get_crash_count(self, date):
        result = self._db.crashstats.find_one({'date': date}, fields = {'_id' : 0, 'count': 1})
        if result is None:
            return 0
        return result['count']
