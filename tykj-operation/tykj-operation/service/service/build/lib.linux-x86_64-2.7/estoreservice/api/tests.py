from __future__ import print_function, division, absolute_import
from bson.objectid import ObjectId
from django.test import TestCase
from estorecore.servemodels.push import PushMongodbStorage
from estoreservice import settings
import logging
import os
import time
from estorecore.test import get_all_test_cases


logger = logging.getLogger('django')


# import all test cases from test directory
test_case_dir = os.path.abspath(
    os.path.join(os.path.abspath(__file__), '..', 'test'))
test_cases = get_all_test_cases(test_case_dir)
for pkg, mod in test_cases:
    exec 'from %s.%s import *' % (pkg, mod)


class SimpleTest(TestCase):

    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


def dtest_push_message_update_perf():
    push_db = PushMongodbStorage(settings.MONGODB_CONF)
    # cond = {'_id': ObjectId("51064adb9813f3ea9cc702bc")}
    cond = {'id': 73}
    n_round = 10
    message_coll = push_db._db.messages

    for msg in message_coll.find(cond):
        print(msg)

    total_time = 0.0
    for _ in range(n_round):
        start = time.time()
        message_coll.update(cond, {'$inc': {'sent_count': 1}})
        total_time += (time.time() - start) * 1000.0

    print('inc sent_count sync took: %0.3f ms' % (total_time / n_round))

    total_time = 0.0
    for _ in range(n_round):
        start = time.time()
        message_coll.update(cond, {'$inc': {'sent_count': 1}}, w=0)
        total_time += (time.time() - start) * 1000.0

    print('inc sent_count async took: %0.3f ms' % (total_time / n_round))

    # Revert above changes.
    message_coll.update(cond, {'$inc': {'sent_count': -1 * 2 * n_round}})


if __name__ == '__main__':
    dtest_push_message_update_perf()
