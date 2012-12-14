"""
settings.py: Settings constants used by the run_python_tests.py plugin.
"""
import os

PYTHON_PROJECT_ROOT_SETTING = 'python_project_root'
TEST_MODE = 'python_test_mode'
TEST_COMMAND_SETTING = 'python_test_command'
TEST_COMMAND_OPTIONS_SETTING = 'python_test_command_options'
TEST_MODULE_SETTING = 'python_test_module'
TEST_TERMINAL_SETTING = 'python_test_terminal'
VIRTUALENV_SETTING = 'python_virtualenv'
PYTHON_TESTS_PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
