from estorecore.db import MongodbStorage, \
                          IncrementalId, \
                          set_default_order, \
                          cursor_to_list, \
                          timestamp_utc_now

class UserTargetingMongodbStorage(MongodbStorage):

    db_name = "usertargeting"

    def __init__(self, conn_str):
        super(UserTargetingMongodbStorage, self).__init__(conn_str, self.db_name)
        self._ids = IncrementalId(self._db)

    @cursor_to_list
    def query_app_graph(self, edges):
        return self._db.tags.find({'_id' : {'$in': edges}}, fields = {'_id': 1, 'score': 1})
