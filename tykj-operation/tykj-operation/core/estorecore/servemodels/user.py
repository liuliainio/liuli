from bson import binary
from estorecore.db import MongodbStorage, \
                          IncrementalId, \
                          set_default_order, \
                          cursor_to_list, \
                          timestamp_utc_now

class UserMongodbStorage(MongodbStorage):

    db_name = "user"

    UPDATE_QUERY_LIMIT_TIME = 60*60 # one hour

    def __init__(self, conn_str):
        super(UserMongodbStorage, self).__init__(conn_str, self.db_name)
        self._ids = IncrementalId(self._db)

    # TODO: security/user check
    def update_apps_installed(self, client_id, user_app_data):
        cond = { '_id': client_id }
        apps = user_app_data.get('apps', None)
        if apps is None:
            return

        apps = [app.get('packageName', '') + ':' + str(app.get('packageVersion', '')) for app in apps]
        data_str = '|'.join(apps)
        data_bytes = data_str.encode('zip')
        data_binary = binary.Binary(data_bytes)

        self._db.apps.installed.update(cond, {'_id': client_id, 'apps': data_binary }, True, w = 0)

    # TODO: security/user check
    def query_apps_installed(self, client_id):
        result = self._db.apps.installed.find_one({'_id' : client_id})
        if not result or isinstance(result['apps'], list):
            return result
        client_id = result.get('_id')
        if not client_id:
            return None

        data_str = result['apps'].decode('zip')
        if data_str:
            items = [item.rsplit(':', 1) for item in data_str.split('|')]
            apps = [{'packageName': item[0], 'packageVersion': int(item[1])} for item in items]
        else:
            apps = []
        result['apps'] = apps

        return result

    def query_user_tags(self, client_id):
        user = self._db.tags.find_one({'_id' : client_id})
        if not user or not 'tags' in user:
            return None

        tags = user['tags']
        if not isinstance(tags, dict):
            # decode tags
            data_str = tags.decode('zip')
            if data_str:
                tags = dict([item.rsplit(':', 1) for item in data_str.split('|')])
            else:
                tags = { }

        return tags


    def set_recommended_apps(self, client_id, apps, time_now):
        data = { }
        for app in apps:
            data[str(app)] = time_now

        self._db.recommendedapps.update({'_id': client_id}, {'$set': data}, True, w = 0)


    def get_recommended_apps(self, client_id):
        data = self._db.recommendedapps.find_one(client_id)
        if data:
            del data['_id']
        return data


    def can_query_update(self, client_id):
        now = timestamp_utc_now()
        limit = self._db.limits.find_and_modify({'_id':client_id}, {'_id':client_id, 'last_query':now }, True)
        if not limit or (now - limit['last_query'] > self.UPDATE_QUERY_LIMIT_TIME):
            return True
        return False
