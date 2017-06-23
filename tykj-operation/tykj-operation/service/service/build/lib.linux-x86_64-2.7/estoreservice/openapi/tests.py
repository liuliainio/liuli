"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from estorecore.test import get_all_test_cases
import os


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
