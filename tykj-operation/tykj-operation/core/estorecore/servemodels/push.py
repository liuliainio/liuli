from estorecore.db import MongodbStorage, IncrementalId, cursor_to_list, timestamp_utc_now
from estorecore.models.constants import MESSAGE_STATUS
from estorecore.utils.simplecache import cached_query

# Reserved message ids: [100 - 9999]
MESSAGE_ID_RESERVED_APPS_UPDATE = 101
# Other message ids start from 10000
MESSAGE_ID_START = 10000

message_fields_detail = {
    '_id': 1,
    'message_id': 1,
    'category': 1,
    'short_message': 1,
    'action': 1,
    'value': 1,
    'created_time': 1,
    'last_modified': 1,
    'status': 1,
    'targets': 1,
}


class PushMongodbStorage(MongodbStorage):

    db_name = "push"

    def __init__(self, conn_str):
        super(PushMongodbStorage, self).__init__(conn_str, self.db_name)
        self._ids = IncrementalId(self._db)

    def is_test_device(self, client_id):
        cond = {
            'client_id': client_id
        }
        return True if self._db.testdevices.find_one(cond) else False

    def _process_target_version_code(self, source, message):
        if not source:
            return message

        tg_version_code = []
        if message.get('targets', {}).get('tg_version_code', {}):
            tg_version_code = message['targets']['tg_version_code'].get(source.replace('.', '_'), [])
        message['targets']['tg_version_code'] = tg_version_code
        return message

    def _get_valid_messages(self):
        now = timestamp_utc_now()

        return cached_query('push_valid_nmessages',
            lambda sender : [message for message in sender._db.messages.find({ 'not_valid_before': {'$lte': now}, 'not_valid_after': {'$gt': now} }, fields = message_fields_detail)],
            query_func_state = self,
            timeout = 120,
            return_cache_hit_status = True)

    def _is_in(self, array, item):
        if not array:
            return True
        if not item:
            return False
        if isinstance(array, list):
            return item in array
        return item == array

    def _filter_messages(self, messages, client_id, source, is_test_device):
        request_message_status = MESSAGE_STATUS.PUBLISHED
        if client_id:
            if is_test_device is None:
                is_test_device = self.is_test_device(client_id)
            if is_test_device:
                request_message_status = MESSAGE_STATUS.PRE_RELEASE

        seen = set()
        final_messages = []
        for message in messages:
            if message.get('message_id', 0) in seen:
                continue
            if message.get('status', 0) < request_message_status:
                continue
            if not self._is_in(message.get('client_id'), client_id):
                continue
            if not self._is_in(message.get('source'), source):
                continue
            message['test'] = message.get('test', 0) + 1
            final_messages.append(message)

        return final_messages

    def query_messages(self, last_query_time, client_id, locale=None, source=None, is_test_device = None):

        messages, cache_hit = self._get_valid_messages()

        messages = self._filter_messages(messages, client_id, source, is_test_device)

        messages = [self._process_target_version_code(source, message) for message in messages]

        return (messages, cache_hit)

    def in_blacklist(self, client_id, user_phone, imei, imsi):
        cond = {'_id': {'$in': [client_id, user_phone, imsi, imei]}}

        return self._db.blacklist2.find_one(cond, fields = {'_id': 1}) is not None


    def get_pushed_messages(self, client_id):
        cond = {
            '_id': client_id
        }
        result = self._db.pushedmessages.find_one(cond, {'_id': 0, 'messages': 1})
        if result and 'messages' in result:
            result = result['messages']
        else:
            result = { }
        return result

    def set_pushed_messages(self, client_id, messages):
        data = {'_id': client_id, 'messages': messages}
        return self._db.pushedmessages.update({'_id': client_id}, data, True, w = 0)

    @cursor_to_list
    def get_message_pushed_counts(self, messages):
        return self._db.pushedcounts.find({'_id': {'$in': [message['message_id'] for message in messages]}})

    def inc_message_pushed_counts(self, date_now_str, messages):
        for message in messages:
            self._db.pushedcounts.update({'_id': message['message_id']}, {'$inc': {'total': 1, date_now_str: 1}}, True, w = 0)

    @cursor_to_list
    def query_message_stats(self, message_id):
        cond = {'message_id': MESSAGE_ID_START + message_id}
        return self._db.statictis.find(cond)

