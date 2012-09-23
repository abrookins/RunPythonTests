"""
tests.py: Unit tests for helpers used by run_python_tests.py.
"""
import os
import settings
import util
import unittest


class UtilTests(unittest.TestCase):

    def setUp(self):
        self.test_files_dir = os.path.join(settings.PYTHON_TESTS_PACKAGE_DIR,
                                           'test_files')

    def test_find_file_finds_one_valid_dir_of_one_valid(self):
        dir = util.find_file(['setup.py'],
                             os.path.join(self.test_files_dir, 'test_app'))
        self.assertEqual(dir, self.test_files_dir)

    def test_find_file_finds_one_valid_dir_of_two_valid(self):
        dir = util.find_file(['setup.py', 'settings.py'],
                             os.path.join(self.test_files_dir, 'test_app'))
        self.assertEqual(dir, self.test_files_dir)

    def test_find_file_finds_one_valid_dir_of_one_valid_one_invalid(self):
        dir = util.find_file(['setup.py', 'not_real.py'],
                             os.path.join(self.test_files_dir, 'test_app'))
        self.assertEqual(dir, self.test_files_dir)

    def test_find_file_returns_none_if_none_valid(self):
        dir = util.find_file(['not_real.py', 'also_not_real.py'],
                             os.path.join(self.test_files_dir, 'test_app'))
        self.assertEqual(dir, None)

    def test_get_django_test_method(self):
        test_name = util.get_django_test('app', 'class', 'fn', 'method')
        self.assertEqual(test_name, 'app.class.fn')

    def test_get_django_test_class(self):
        test_name = util.get_django_test('app', 'class', 'fn', 'class')
        self.assertEqual(test_name, 'app.class')

    def test_get_django_test_suite(self):
        test_name = util.get_django_test('app', 'class', 'fn', 'suite')
        self.assertEqual(test_name, 'app')

    def test_get_nose_test_method(self):
        test_name = util.get_nose_test('app', 'class', 'fn', 'method')
        self.assertEqual(test_name, 'app.tests:class.fn')

    def test_get_nose_test_class(self):
        test_name = util.get_nose_test('app', 'class', 'fn', 'class')
        self.assertEqual(test_name, 'app.tests:class')

    def test_get_nose_test_suite(self):
        test_name = util.get_nose_test('app', 'class', 'fn', 'suite')
        self.assertEqual(test_name, 'app.tests')

    def test_get_setup_py_test_method(self):
        test_name = util.get_setup_py_test('app', 'class', 'fn', 'method')
        self.assertEqual(test_name, '')

    def test_get_setup_py_test_class(self):
        test_name = util.get_setup_py_test('app', 'class', 'fn', 'class')
        self.assertEqual(test_name, '')

    def test_get_setup_py_test_suite(self):
        test_name = util.get_setup_py_test('app', 'class', 'fn', 'suite')
        self.assertEqual(test_name, '')
