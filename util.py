"""
util.py: Utility functions for run_python_tests.py.
"""
import class_finder
import os
import settings
import subprocess

from terminal_selector import TerminalSelector


def find_dir_containing(filenames, starting_dir):
    """
    Recursively check the current and then parent directory for filenames in the
    iterable `filenames`, starting from `starting_dir`.

    Returns the directory containing one of `filenames` or None if not found.
    The name should probably reflect this behavior.
    """
    exists = False

    for filename in filenames:
        exists = os.path.exists(os.path.join(starting_dir, filename))
        if exists:
            break

    if exists:
        return starting_dir
    elif starting_dir == os.path.sep:
        # Stop if `starting_dir` is the root directory, identified on UNIX/Linux
        # systems as '/'
        return None
    else:
        return find_dir_containing(
            filenames,
            os.path.abspath(os.path.dirname(starting_dir)))


def find_project_root(filename):
    """
    Return the name of the first directory up from ``filename`` that contains
    either a `settings.py` or `setup.py` file.

    This is our best guess for the project root for ``filename``.
    """
    return find_dir_containing(
        ['settings.py', 'setup.py'], os.path.dirname(filename))


def find_package(filename):
    """
    Return the package containing ``filename``.
    """
    return find_dir_containing(['__init__.py'], os.path.dirname(filename))


def find_django_app_dir(filename):
    """
    Find the Django app directory containing ``filename``.
    """
    return find_dir_containing(['models.py', 'models'], filename)


def find_django_app_name(filename):
    app_dir = find_django_app_dir(filename)

    if app_dir:
        return os.path.dirname(app_dir)


def make_import_string(filename):
    """
    Return a Python import string for ``filename`` that starts with the root
    package ``root_package``.
    """
    path_parts = filename.split(os.path.sep)
    import_string = '.'.join(path_parts)
    return import_string.rstrip('.py')


def get_current_test_function(view):
    """
    Return the name of the first test function (a function that starts with
    'test_') found above the current line.
    """
    sel = view.sel()[0]
    entities = view.find_by_selector('entity.name.function')
    current_entity = None

    for e in reversed(entities):
        if e.a < sel.a and view.substr(e).startswith('test_'):
            current_entity = view.substr(e)
            break

    return current_entity


def get_django_test(view, target):
    test_fn = get_current_test_function(view)

    # Test functions must start with `test_`.
    if test_fn and test_fn.startswith('test_') is False:
        return

    filename = view.file_name()
    test_cls = class_finder.find_class(filename, test_fn)
    app_name = find_django_app_name(filename)
    test_name = None

    if target == 'method':
        test_name = '%s.%s.%s' % (app_name, test_cls, test_fn)
    elif target == 'class':
        test_name = '%s.%s' % (app_name, test_cls)
    elif target == 'suite':
        test_name = app_name

    return test_name


def get_nose_test(view, target):
    test_fn = get_current_test_function(view)

    # Test functions must start with `test_`.
    if test_fn and test_fn.startswith('test_') is False:
        return

    filename = view.file_name()
    test_cls = class_finder.find_class(filename, test_fn)
    project_root = find_project_root(filename)
    filename = filename[len(project_root):]
    filename = filename.lstrip(os.path.sep)
    import_string = make_import_string(filename)
    test_name = None

    if target == 'method':
        test_name = '%s:%s.%s' % (import_string, test_cls, test_fn)
    elif target == 'class':
        test_name = '%s:%s' % (import_string, test_cls)
    elif target == 'suite':
        test_name = import_string

    return test_name


def get_setup_py_test(view, target):
    return ''


test_formats = {
    'django': get_django_test,
    'nose': get_nose_test,
    'setup.py': get_setup_py_test
}


def get_test_name(view, mode, target='method'):
    """
    Get the name of the nearest test to run above the cursor, identified by
    `target`, which can be 'method', 'class', or 'suite'.

    Using 'method' returns the name of the individual test enclosing the cursor.

    Using 'class' returns the name of the test class enclosing the test method
    in which the cursor rests.

    Using 'suite' returns the name of the package, which should cause the test
    runner to run the package's suite of tests.
    """
    formatter = test_formats.get(mode, None)

    if not formatter:
        return

    test_name = formatter(view, target)

    return test_name


test_modules = {
    'django': 'manage.py',
    'setup.py': 'setup.py'
}

test_commands = {
    'django': 'test',
    'nose': '',
    'setup.py': 'test -q'
}


def get_test_command(mode, view_settings, filename):
    default_test_module = test_modules.get(mode, None)
    default_test_command = test_commands.get(mode, None)
    project_root = None

    test_cmd = view_settings.get(
        settings.TEST_COMMAND_SETTING, default_test_command)
    test_cmd_options = view_settings.get(settings.TEST_COMMAND_OPTIONS_SETTING)
    test_module = view_settings.get(
        settings.TEST_MODULE_SETTING, default_test_module)

    virtualenv = view_settings.get(settings.VIRTUALENV_SETTING, None)

    # User can override this with a setting if necessary. Otherwise, we'll
    # try to discover the Python project's root directory.
    full_test_command = None

    if mode == 'nose':
        full_test_command = "nosetests"
    else:
        project_root = view_settings.get(settings.PYTHON_PROJECT_ROOT_SETTING)

        if project_root is None:
            project_root = find_project_root(filename)

        if project_root:
            full_test_command = 'python %s %s' % (
                os.path.join(project_root, test_module), test_cmd)

    if virtualenv:
        full_test_command = 'venvwrapper && workon %s && %s %s' % (
            virtualenv, full_test_command, test_cmd_options)

    return full_test_command


def run_shell_command(cmd):
    return subprocess.Popen(
        [cmd],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
    ).communicate()


def run_test_command(test_cmd, test_name, terminal):
    cmd = '"%s" "%s %s"' % (
        TerminalSelector.get(terminal), test_cmd, test_name)

    return run_shell_command(cmd)
