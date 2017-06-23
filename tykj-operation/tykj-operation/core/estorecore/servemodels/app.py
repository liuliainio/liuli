# -*- coding: utf-8 -*-
import pymongo
from estorecore.db import MongodbStorage, IncrementalId, set_default_order, \
        cursor_to_list, timestamp_utc_now

APPLIST_ITEM_TYPE_APPDETAIL = 3

APP_FIELDS_RATING = {
    '_id': 1,
    'rate': 1,
    'rate_count': 1
}

APP_FIELDS_ID = {
    '_id': 0,
    'id': 1,
    'tid':1,
    'download_tid':1,
    'backup_tid':1,
}

APP_FIELDS_LIST_SIMPLE = {
    '_id': 0,
    'id': 1,
    'tid':1,
    'download_tid':1,
    'backup_tid':1,
    'name': 1,
    'icon_url': 1,
    'rate': 1,
    'download_count': 1,
    'size': 1,
    'version': 1,
}

APP_FIELDS_LIST_MEDIUM = {
    '_id': 0,
    'id': 1,
    'tid':1,
    'download_tid':1,
    'backup_tid':1,
    'name': 1,
    'icon_url': 1,
    'rate': 1,
    'download_count': 1,
    'size': 1,
    'version': 1,
    'version_code': 1,
    'package_name': 1,
    "package_sig": 1,
    'developer': 1,
    'min_sdk_version': 1,
    'max_sdk_version': 1,
    'boot_app_type': 1,
    'safe_type': 1,
    'safe_verifiers': 1,
    'ad_type': 1,
    'ad_tags': 1,
    'privacy_type': 1,
    'privacy_tags': 1,
    'other_tags': 1,
    'short_desc': 1,
}

APP_FIELDS_LIST_DETAILS = {
    '_id': 0,
    'id': 1,
    'tid':1,
    'download_tid':1,
    'backup_tid':1,
    'name': 1,
    'icon_url': 1,
    'rate': 1,
    'download_count': 1,
    'size': 1,
    'version': 1,
    'version_code': 1,
    'package_name': 1,
    "package_sig": 1,
    'developer': 1,
    'description': 1,
    'preview_icon_urls': 1,
    'related_apps': 1,
    'update_date': 1,
    'cate_name': 1,
    'category_id': 1,
    'price': 1,
    'safe_type': 1,
    'safe_verifiers': 1,
    'ad_type': 1,
    'ad_tags': 1,
    'privacy_type': 1,
    'privacy_tags': 1,
    'other_tags': 1,
    'sub_category_id': 1,
    'package_hash': 1,
}

APP_FIELDS_DOWNLOAD = {
    '_id': 1,
    'download_url': 1,
    'download_url2': 1,
    'package_name': 1,
    'version_code': 1,
    'package_hash': 1,
}

RECOMMEND_FIELDS_DETAILS = {
    '_id': 0,
    'id': 1,
    'tid':1,
    'download_tid':1,
    'backup_tid':1,
    'name': 1,
    'icon_url': 1,
    'rate': 1,
    'size': 1,
    'package_name': 1,
    'version': 1,
    'version_code': 1,
    'download_count': 1,
    'price': 1,
    'sub_cate_name': 1,
    'safe_type': 1,
    'safe_verifiers': 1,
    'ad_type': 1,
    'ad_tags': 1,
    'privacy_type': 1,
    'privacy_tags': 1,
    'other_tags': 1,
}

APP_LIST_ITEM_FIELDS_DETAILS = {
    '_id': 0,
    'id': 1,
    'tid':1,
    'download_tid':1,
    'backup_tid':1,
    'name': 1,
    'icon_url': 1,
    'large_icon_url': 1,
    'rate': 1,
    'size': 1,
    'package_name': 1,
    'version': 1,
    'version_code': 1,
    'download_count': 1,
    'price': 1,
    'description': 1,
    'preview_icon_urls': 1,
    'cate_name': 1,
    'category_id': 1,
    'min_sdk_version': 1,
    'max_sdk_version': 1,
    'safe_type': 1,
    'safe_verifiers': 1,
    'ad_type': 1,
    'ad_tags': 1,
    'privacy_type': 1,
    'privacy_tags': 1,
    'other_tags': 1,
}

RICH_ITEM_FILEDS = {
    '_id': 0,
    'order': 1,
    'title': 1,
    'description': 1,
    'icon_url': 1,
    'attr': 1,
    'type': 1,
}

REVIEW_FIELDS_DETAILS = {
    '_id': 0,
    'id': 1,
    'user_id': 1,
    'user_name': 1,
    'rate': 1,
    'comment': 1,
    'created_time': 1
}

SUBJECT_ITEM_FIELDS = {
    '_id': 0,
    'id': 1,
    'subject_id': 1,
    'order': 1,
    'title': 1,
    'description': 1,
    'apps': 1,
    'icon_url': 1,
    'subject_info': 1,
}

KUWAN_ITEM_FIELDS = {
    '_id': 0,
    'id': 1,
    'order': 1,
    'title': 1,
    'description': 1,
    'icon_url': 1,
    'price': 1,
    't_id': 1,
    'list_type': 1,
}

KUWAN_APP_LIST_FIELDS = {
    '_id': 0,
    'apps': 1,
}


class AppMongodbStorage(MongodbStorage):

    db_name = "app"

    #CATEGORY_APPS_ORDER_DOWNLOADS = "download_count"
    CATEGORY_APPS_ORDER_DOWNLOADS = "order"
    CATEGORY_APPS_ORDER_RATING = "rate"

    RECOMMENDS_ORDER = 'order'
    RECOMMEND_TYPE_NEWEST = 10
    RECOMMEND_TYPE_HOTEST = 11
    RECOMMEND_TYPE_BESTMATCH = 12
    RECOMMEND_TYPE_HOMENEW = 13

    AREA_RECOMMEND = 2
    AREA_TOP = 1
    AREA_CATEGORY = 3

    def __init__(self, conn_str):
        super(AppMongodbStorage, self).__init__(conn_str, self.db_name)
        self._ids = IncrementalId(self._db)

        self._db.categories.ensure_index("parent_category_id")
        self._db.tops.ensure_index("category_id")

        self._db.apps.ensure_index([("sub_category_id", pymongo.ASCENDING), ("download_count", pymongo.DESCENDING)])
        self._db.apps.ensure_index("id")
        self._db.apps.ensure_index("tid")
        self._db.apps.ensure_index("download_tid")
        self._db.apps.ensure_index("package_sig")
        self._db.apps.ensure_index("sub_category_id")
        self._db.apps.ensure_index("package_name")

        self._db.reviews.ensure_index([("app_id", pymongo.ASCENDING), ("created_time", pymongo.DESCENDING)])

        self._db.recommends.ensure_index([("type", pymongo.ASCENDING), (self.RECOMMENDS_ORDER, pymongo.ASCENDING)])
        self._db.focus_images.ensure_index([("area", pymongo.ASCENDING), ('category_id', pymongo.ASCENDING), ('order', pymongo.ASCENDING)])
        self._db.focus_images.ensure_index([("area", pymongo.ASCENDING), ('recommend_type', pymongo.ASCENDING), ('order', pymongo.ASCENDING)])

    @cursor_to_list
    @set_default_order
    def query_categories(self, parent_category_id=0, level=1, start_index=0, count=20, order=None):
        cond = {'parent_category_id': parent_category_id}  # current only support get l level sub category
        return self._db.categories.find(cond, skip=start_index, limit=count, sort=order)

    @cursor_to_list
    @set_default_order
    def query_category_tops(self, category_id, start_index=0, count=20, order=None):
        cond = {'category_id': category_id}
        return self._db.tops.find(cond, skip=start_index, limit=count, sort=order, fields=APP_FIELDS_LIST_MEDIUM)

    @cursor_to_list
    @set_default_order
    def query_category_apps(self, category_id=0, start_index=0, count=20, order=None):
        if not order:
            order = [('download_count', self.ORDER_DESC)]
        else:
            if isinstance(order, str):
                order = [(order, self.ORDER_ASC if order == self.CATEGORY_APPS_ORDER_DOWNLOADS else self.ORDER_DESC)]
        cond = {'sub_category_id': category_id}
        return self._db.apps.find(cond, skip=start_index, limit=count, sort=order, fields=APP_FIELDS_LIST_MEDIUM)

    @cursor_to_list
    @set_default_order
    def query_category_focus_images(self, category_id, recommend_type, area, start_index=0, count=20, order=None):
        if order is None:
            order = [('order', self.ORDER_ASC)]
        if category_id > 0:
            cond = {'area': area, 'category_id': category_id}
        else:
            cond = {'area': area, 'recommend_type': recommend_type}
        return self._db.focus_images.find(cond, skip=start_index, limit=count, sort=order)

    @cursor_to_list
    @set_default_order
    def query_subjects(self, start_index=0, count=20, order=None):
        return self._db.subjects.find({}, skip=start_index, limit=count, sort=order)

    @cursor_to_list
    @set_default_order
    def query_subject_apps(self, subject_id, start_index=0, count=20, order=None):
        cond = {'subject_id': subject_id}
        return self._db.subject_apps.find(cond, skip=start_index, limit=count, sort=order, fields=SUBJECT_ITEM_FIELDS)

    @cursor_to_list
    @set_default_order
    def query_kuwan_items(self, start_index=0, count=20, order=None):
        return self._db.kuwan_items.find({}, skip=start_index, limit=count, sort=order, fields=KUWAN_ITEM_FIELDS)

    @cursor_to_list
    @set_default_order
    def query_kuwan_app_list(self, kuwan_id, start_index=0, count=20, order=None):
        cond = {'id': kuwan_id}
        return self._db.kuwan_items.find(cond, skip=start_index, limit=count, sort=order, fields=KUWAN_APP_LIST_FIELDS)

    def get_info(self, app_id):
        cond = {'id': app_id}
        return self._db.apps.find_one(cond, fields=APP_FIELDS_LIST_DETAILS)

    def get_info_by_tid(self, app_tid):
        cond = {'backup_tid': app_tid}
        return self._db.apps.find_one(cond, fields=APP_FIELDS_LIST_DETAILS)

    def get_app_by_package(self, package_name):
        cond = {'package_name': package_name}
        return self._db.apps.find_one(cond, fields = APP_FIELDS_LIST_DETAILS)

    def get_info_for_related_apps(self, app_id_list, count=10):
        cond = {'id': {'$in': app_id_list}}
        related_apps = self._db.apps.find(cond, limit=count, fields=APP_FIELDS_LIST_SIMPLE)

        # Since we use $in operator to query, ordering is not preserved in returned result.
        # In order to preserve the related app ordering in app_id_list, we use an extra dict to do the lookup.
        related_apps_dict = dict((app['id'], app) for app in related_apps)
        return [related_apps_dict[app_id] for app_id in app_id_list if app_id in related_apps_dict]

    def get_info_for_same_developer_apps(self, developer_package_sig, exclude_app_id=0, count=10):
        cond = {'package_sig': developer_package_sig}
        results = self._db.apps.find(cond, limit=count, fields=APP_FIELDS_LIST_SIMPLE)
        results = [x for x in results if x['id'] != exclude_app_id]
        results = sorted(results, key = lambda x: x['download_count'], reverse=True)
        return results

    def get_download_info(self, app_id):
        cond = {'id': app_id}
        # remove {'$inc': {'download_count': 1}}, : we will count the downloads offline
        result = self._db.apps.find_one(cond, fields=APP_FIELDS_DOWNLOAD)
        return result

    def get_app_backup_tid(self, app_id):
        cond = {'id': app_id}
        # remove {'$inc': {'download_count': 1}}, : we will count the downloads offline
        result = self._db.apps.find_one(cond, fields={'_id': 0, 'backup_tid': 1})
        if result:
            result = result['backup_tid']
        return result

    @cursor_to_list
    @set_default_order
    def query_recommends(self, start_index=0, count=20, recommend_type=RECOMMEND_TYPE_NEWEST, order=None):
        if not order:
            order = [(self.RECOMMENDS_ORDER, self.ORDER_ASC)]
        return self._db.recommends.find({'type': recommend_type}, skip=start_index, limit=count, sort=order, fields=RECOMMEND_FIELDS_DETAILS)

    def is_home_new(self, app_id):
        return self._db.recommends.find({'id': app_id, 'type': self.RECOMMEND_TYPE_HOMENEW}, limit=1).count() > 0

    @cursor_to_list
    @set_default_order
    def query_must_haves(self, start_index=0, count=20, order=None):
        return self._db.must_haves.find({}, skip=start_index, limit=count, sort=order, fields=APP_FIELDS_LIST_MEDIUM)

    @cursor_to_list
    @set_default_order
    def query_boot_apps(self, client_id, os, device_name, device_type, resolution, start_index=0, count=20, order=None):
        return self._db.bootapps.find({}, skip=start_index, limit=count, sort=order, fields=APP_FIELDS_LIST_MEDIUM)

    @cursor_to_list
    @set_default_order
    def query_extra_boot_apps(self, client_id, os, device_name, device_type, resolution, start_index=0, count=20, order=None):
        return self._db.extrabootapps.find({}, skip=start_index, limit=count, sort=order, fields=APP_FIELDS_LIST_MEDIUM)

    def query_app_lists(self):
        results = self._db.app_lists.find({})
        type_dict = {}
        for t in results:
            type_dict[str(t['id'])] = t['id']
            type_dict[str(t['codename'])] = t['id']

        return type_dict

    def _try_parse_app_list_id(self, app_list_id):
        try:
            app_list_id = int(app_list_id)
        except:
            app_list = self._db.app_lists.find_one({'codename': app_list_id})
            if app_list:
                return app_list['id']
        else:
            return app_list_id
        return None

    def _convert_extra_infos(self, extra_infos):
        if 'views_count' in extra_infos:
            if extra_infos['views_count'] >= 10000:
                extra_infos['display_views_count'] = u'%d万+' % (extra_infos['views_count'] / 10000)
            elif extra_infos['views_count'] >= 1000:
                extra_infos['display_views_count'] = u'%d千+' % (extra_infos['views_count'] / 1000)
            else:
                extra_infos['display_views_count'] = u'<1千'
        return extra_infos

    def _convert_app_list_items(self, results, fields):
        r_list = []
        for r in results:
            cr = {}
            if 'extra_infos' in r:
                cr['extra_infos'] = self._convert_extra_infos(r['extra_infos'])
            if 'image_url' in r:
                cr['image_url'] = r['image_url']

            if 'app' in r:
                if 'id' in r['app']:
                    cr['id'] = r['app']['id']
                for f in [k for k, v in fields.iteritems() if v == 1]:
                    if f in r['app']:
                        cr[f] = r['app'][f]
                    elif f == 'large_icon_url':
                        cr[f] = r['large_icon_url']
            else:
                for f in [k for k, v in RICH_ITEM_FILEDS.iteritems() if v == 1]:
                    if f in r:
                        cr[f] = r[f]
                if 'attr' in r and r['type'] == APPLIST_ITEM_TYPE_APPDETAIL:
                    cr['id'] = int(r['attr'])
                else:
                    cr['id'] = int(r['pk'])
            r_list.append(cr)
        return r_list

    @set_default_order
    def query_apps_from_list(self, app_list_id=None, start_index=0, count=20, order=None, fields=APP_LIST_ITEM_FIELDS_DETAILS):
        app_list_id = self._try_parse_app_list_id(app_list_id)
        if app_list_id is None:
            return []
        cond = {'app_list_id': app_list_id}
        results = self._db.app_list_items.find(cond, skip=start_index, limit=count, sort=order)
        results = self._convert_app_list_items(results, fields)
        return results

    # parameter: app_list: list of package_names
    @cursor_to_list
    def query_updates(self, app_list):
        if not app_list:
            return []

        if isinstance(app_list[0], dict):
            # support old app update API
            app_list = [app['packageName'] for app in app_list]

        cond = { 'package_name': {'$in': app_list} }
        fields = APP_FIELDS_LIST_MEDIUM.copy()
        fields.update({'package_hash': 1})
        return self._db.apps.find(cond, fields=fields)

    @cursor_to_list
    def query_reviews(self, app_id, start_index=0, count=20, order=None):
        if order is None:
            order = [('created_time', self.ORDER_DESC)]
        cond = {'app_id': app_id}
        return self._db.reviews.find(cond, skip=start_index, limit=count, sort=order, fields=REVIEW_FIELDS_DETAILS)

    def save_reviews(self, reviews):
        for review in reviews:
            try:
                review.update({
                        'id': self._ids.next_id("reviews"),
                        'user_id': int(review.get('user_id', 0)),
                        'user_name': review.get('user_name', ''),
                        'app_id': int(review.get('app_id', 0)),
                        'rate': float(review.get('rate', 0)),
                        'comment': review.get('comment', ''),
                        'created_time': timestamp_utc_now()
                    })
                self._db.reviews.save(review)
            except Exception, e:
                print e
                continue

            if review['app_id'] == 0:
                continue

            app = self._db.apps.find_one({'id': review['app_id']}, fields=APP_FIELDS_RATING)
            if app is None:
                continue

            self._db.reviews.save(review)

            app_rate_count = app['rate_count'] if 'rate_count' in app else 0
            app_rate = app['rate'] if 'rate' in app else 0
            app_rate = (app_rate + review['rate']) / (app_rate_count + 1.0)
            self._db.apps.update({'_id': app['_id']}, {'$set': {'rate': app_rate, 'rate_count': app_rate_count}})

    @cursor_to_list
    def get_need_sync_reviews(self, start_time):
        return self._db.reviews.find({'created_time': {'$gt': start_time}})

    def get_device_app_blacklist(self, device_model):
        data = self._db.deviceappblacklist.find_one({'_id': device_model})
        if not data:
            return set()
        return set(data['apps'])
