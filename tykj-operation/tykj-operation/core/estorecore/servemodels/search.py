from estorecore.db import MongodbStorage, set_default_order, cursor_to_list


class SearchMongodbStorage(MongodbStorage):

    db_name = "search"
    SORT_ORDER = 'order'

    def __init__(self, conn_str):
        super(SearchMongodbStorage, self).__init__(conn_str, self.db_name)

    def fetch_hot_keywords_safe(self, results, start_index, count, order):
        for result in self._db.hot_keywords.find({}, skip=start_index, limit=count, sort=order):
            results.append(result)

    @set_default_order
    def query_hot_keywords(self, start_index=0, count=20, order=None):
        if not order:
            order = [(self.SORT_ORDER, self.ORDER_ASC)]
        results = []
        if start_index > 0:
            total = self._db.hot_keywords.count()
            if total == 0:
                return results
            self.fetch_hot_keywords_safe(results, start_index % total, count, order)
            if len(results) < count and total >= count:
                self.fetch_hot_keywords_safe(results, 0, count - len(results), order)
        else:
            self.fetch_hot_keywords_safe(results, start_index, count, order)
        return results
