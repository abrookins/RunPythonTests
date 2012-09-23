"""
util.py: Utility functions for run_python_tests.py.
"""
import class_finder
import os
import settings
import subprocess

from terminal_selector import TerminalSelector


def find_file(filenames, starting_dir):
    """
    Recursively check the current and then parent directory for filenames in the
    iterable `filenames`, starting from `starting_dir`.

    Returns the directory containing one of `filenames` or None if not found.
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
        return find_file(filenames, os.path.dirname(starting_dir))


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


def get_django_test(app_name, test_cls, test_fn, target):
    test_name = None

    if target == 'method':
        test_name = '%s.%s.%s' % (app_name, test_cls, test_fn)
    elif target == 'class':
        test_name = '%s.%s' % (app_name, test_cls)
    elif target == 'suite':
        test_name = app_name

    return test_name


def get_nose_test(app_name, test_cls, test_fn, target):
    test_name = None

    if target == 'method':
        test_name = '%s.tests:%s.%s' % (app_name, test_cls, test_fn)
    elif target == 'class':
        test_name = '%s.tests:%s' % (app_name, test_cls)
    elif target == 'suite':
        test_name = "%s.tests" % app_name

    return test_name


def get_setup_py_test(app_name, test_cls, test_fn, target):
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
    test_fn = get_current_test_function(view)
    test_cls = class_finder.find_class(view.file_name(), test_fn)
    test_name = None

    # XXX: This is a hack to find the package name. Instead we should backtrack
    # from the test test file to the project dir and keep track of the immediate
    # last package, then ue that package name.
    package_name = find_file(['models.py', 'models'], view.file_name())

    # Get the last directory in an absolute path, e.g. `app_name` in the path
    # /one/two/three/app_name.
    if package_name:
        package_name = package_name.split(os.path.sep)[-1]

    # Test functions must start with `test_`.
    if test_fn.startswith('test_') is False:
        return

    formatter = test_formats.get(mode, None)

    if not formatter:
        return

    test_name = formatter(package_name, test_cls, test_fn, target)

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

    test_cmd = view_settings.get(
        settings.TEST_COMMAND_SETTING, default_test_command)
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
            project_root = find_file(
                ['settings.py', 'setup.py'],
                os.path.dirname(filename))

        if project_root:
            full_test_command = 'python %s %s' % (
                os.path.join(project_root, test_module), test_cmd)

    if virtualenv:
        full_test_command = 'venvwrapper && workon %s && %s' % (
            virtualenv, full_test_command)

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
