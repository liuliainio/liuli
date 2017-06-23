import math
import time
import urllib2
import simplejson
from estorecore.db import MongodbStorage, IncrementalId, set_default_order, \
        cursor_to_list, timestamp_utc_now


app_id_dict = {
    'tianyi':'2cd2d9f5af024f218a027ee828015f3e'
    }

class PromotionMongodbStorage(MongodbStorage):
    app_dev_id = '2cd2d9f5af024f218a027ee828015f3e'
    db_name = "promotion"

    def __init__(self, conn_str):
        super(PromotionMongodbStorage, self).__init__(conn_str, self.db_name)
        self._ids = IncrementalId(self._db)

    @cursor_to_list
    @set_default_order
    def query_login_pictures(self, start_index=0, count=20, order=None):
        if order is None:
            order = [('start_date', self.ORDER_DESC)]
        now = timestamp_utc_now()
        cond = {'start_date': {'$lte': now}, 'end_date': {'$gt': now}}
        return self._db.login_pictures.find(cond, skip = start_index, limit = count, sort = order)

    @cursor_to_list
    @set_default_order
    def query_activities(self, start_index=0, count=20, order=None):
        return self._db.activities.find({}, skip=start_index, limit=count, sort=order)



    @cursor_to_list
    def get_need_sync_feedbacks(self, start_time):
        return self._db.feedbacks.find({'created_time': {'$gt': start_time}})

    def transfer_time(self, time_min):
        if time_min < 5:
            return "5m"
        elif time_min > 5 and time_min <= 10:
            return "10m"
        elif time_min > 10 and time_min <= 30:
            return "30m"
        elif time_min > 30 and time_min <= 60:
            return "1h"
        elif time_min > 60 and time_min <= 120:
            return "2h"
        elif time_min > 120 and time_min <= 720:
            return "12h"
        elif time_min > 720 and time_min <= 8640:
            return str(math.floor(time_min / 1440) + 1) + "d"
        elif time_min > 8640 and time_min <= 30240:
            return str(math.floor(time_min / 10080) + 1) + "w"
        elif time_min > 30240 and time_min <= 443520:
            return str(math.floor(time_min / 40320) + 1) + "mon"
        elif time_min > 443520:
            return str(math.floor(time_min / 525600) + 1) + "y"
