"""
tests.py: Unit tests for helpers used by run_python_tests.py.
"""
import functools
import os
import settings
import util
import unittest


class UtilTests(unittest.TestCase):

    def setUp(self):
        class MockView(object):
            def file_name(self):
                return os.path.join(
                    settings.PYTHON_TESTS_PACKAGE_DIR,
                    'test_files', 'test_app', 'tests.py')

        self.mock_view = MockView()

        self.orig_get_current_test_function = util.get_current_test_function
        util.get_current_test_function = lambda view: 'test_fake'

        self.test_files_dir = os.path.join(settings.PYTHON_TESTS_PACKAGE_DIR,
                                           'test_files')

    def tearDown(self):
        util.get_current_test_function = self.orig_get_current_test_function

    def test_find_file_finds_one_valid_dir_of_one_valid(self):
        dir = util.find_dir_containing(['setup.py'],
                             os.path.join(self.test_files_dir, 'test_app'))
        self.assertEqual(dir, self.test_files_dir)

    def test_find_file_finds_one_valid_dir_of_two_valid(self):
        dir = util.find_dir_containing(['setup.py', 'settings.py'],
                             os.path.join(self.test_files_dir, 'test_app'))
        self.assertEqual(dir, self.test_files_dir)

    def test_find_file_finds_one_valid_dir_of_one_valid_one_invalid(self):
        dir = util.find_dir_containing(['setup.py', 'not_real.py'],
                             os.path.join(self.test_files_dir, 'test_app'))
        self.assertEqual(dir, self.test_files_dir)

    def test_find_file_returns_none_if_none_valid(self):
        dir = util.find_dir_containing(['not_real.py', 'also_not_real.py'],
                             os.path.join(self.test_files_dir, 'test_app'))
        self.assertEqual(dir, None)

    def test_get_django_test_method(self):
        test_name = util.get_test_name(self.mock_view, 'django', 'method')
        expected = '%s/test_files.FakeTestClass.test_fake' % \
                   os.path.dirname(__file__)
        self.assertEqual(expected, test_name)

    def test_get_nose_test_method(self):
        test_name = util.get_test_name(self.mock_view, 'nose', 'method')
        self.assertEqual('test_app.tests:FakeTestClass.test_fake', test_name)
