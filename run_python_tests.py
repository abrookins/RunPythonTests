# run_python_tests: Run the Python test nearest to the cursor.
#
# Tests are launched in an external shell, such as iTerm, Terminal.app or
# Konsole.
#
# This code is licensed under the MIT license and copyright (c) Andrew Brookins
# <a.m.brookins@gmail.com>.
#
# The `TerminalSelector` class was extracted from the Sublime Terminal plugin
# and modified slightly. All of Sublime Terminal is licensed under the MIT
# license and copyright (c) 2011 Will Bond <will@wbond.net>

import ast
import os
import sublime_plugin
import subprocess
import sys


PYTHON_PROJECT_ROOT_SETTING = 'python_project_root'
TEST_MODE = 'python_test_mode'
TEST_COMMAND_SETTING = 'python_test_command'
TEST_MODULE_SETTING = 'python_test_module'
TEST_TERMINAL_SETTING = 'python_test_terminal'
VIRTUALENV_SETTING = 'python_virtualenv'
PYTHON_TESTS_PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))


def find_file(filenames, starting_dir):
    """
    Recursively check the current and then parent directory for filenames in the
    iterable `filenames`, starting from `starting_dir`.

    Returns the directory containing `filename` or None if not found.
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


def get_current_test_function(view, entity_selector):
    """
    Return the name of the first test function (a function that starts with
    'test_') found above the current line.
    """
    sel = view.sel()[0]
    entities = view.find_by_selector(entity_selector)
    current_entity = None

    for e in reversed(entities):
        if e.a < sel.a and view.substr(e).startswith('test_'):
            current_entity = view.substr(e)
            break

    return current_entity


class MethodVisitor(ast.NodeVisitor):
    """
    An `ast.NodeVisitor` subclass that finds the enclosing class object for
    `method_name` and saves it in `self.parent_class`.
    """
    def __init__(self, method_name):
        self.method_name = method_name
        self.parent_class = None

    def visit(self, node,  parent=None):
        """
        Visit a node. Optionally supports passing the parent node `parent`.
        """
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node, parent=parent)

    def visit_FunctionDef(self, node, parent=None):
        """
        Store the name of the enclosing class for `self.method_name` if it
        exists within a class.
        """
        if node.name == self.method_name:
            if parent:
                self.parent_class = parent.name
        super(MethodVisitor, self).generic_visit(node)

    def generic_visit(self, node, parent=None):
        """
        Override `NodeVisitor.generic_visit` to pass the parent node into the
        callback for the node we are visiting.
        """
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        self.visit(item, parent=node)
            elif isinstance(value, ast.AST):
                self.visit(value, parent=node)


def get_class_name(filename, method_name):
    """
    Get the name of the enclosing class for `method_name` within `filename`, a
    Python module.
    """
    module = open(filename).read()
    tree = ast.parse(module)
    visitor = MethodVisitor(method_name)
    visitor.visit(tree)
    return visitor.parent_class


def get_test_format_django(app_name, test_cls, test_fn, target):
    test_name = None

    if target == 'method':
        test_name = '%s.%s.%s' % (app_name, test_cls, test_fn)
    elif target == 'class':
        test_name = '%s.%s' % (app_name, test_cls)
    elif target == 'suite':
        test_name = app_name

    return test_name


def get_test_format_nose(app_name, test_cls, test_fn, target):
    test_name = None

    if target == 'method':
        test_name = '%s.tests:%s.%s' % (app_name, test_cls, test_fn)
    elif target == 'class':
        test_name = '%s.tests:%s' % (app_name, test_cls)
    elif target == 'suite':
        test_name = "%s.tests" % app_name

    return test_name


def get_test_format_setup_py(app_name, test_cls, test_fn, target):
    return ''


test_formats = {
    'django': get_test_format_django,
    'nose': get_test_format_nose,
    'setup.py': get_test_format_setup_py
}


def get_test_name(view, mode, target='method'):
    """
    Get the name of the nearest test to run above the cursor, identified by
    `target`, which can be 'method', 'class', or 'suite'.

    Using 'method' returns the name of the individual test enclosing the cursor.

    Using 'class' returns the name of the test class enclosing the test method
    in which the cursor rests.

    Using 'suite' returns the name of the app, which should cause the test
    runner to run the entire app's suite of tests.
    """
    test_fn = get_current_test_function(view, 'entity.name.function')
    test_cls = get_class_name(view.file_name(), test_fn)
    app_name = find_file(['models.py', 'models'], view.file_name())
    test_name = None

    # The path is, e.g., /one/two/three/app_name, so get `app_name`.
    if app_name:
        app_name = app_name.split(os.path.sep)[-1]

    # Test functions must start with `test_`.
    if test_fn.startswith('test_') is False:
        return

    formatter = test_formats.get(mode, None)

    if not formatter:
        return

    test_name = formatter(app_name, test_cls, test_fn, target)

    return test_name


class NotFoundError(Exception):
    pass


class TerminalSelector(object):
    default = None

    @staticmethod
    def get(terminal=None):
        if terminal:
            dir, executable = os.path.split(terminal)
            if not dir:
                joined_terminal = os.path.join(
                    PYTHON_TESTS_PACKAGE_DIR, executable)
                if os.path.exists(joined_terminal):
                    terminal = joined_terminal
                    if not os.access(terminal, os.X_OK):
                        os.chmod(terminal, 0755)
            return terminal

        if TerminalSelector.default:
            return TerminalSelector.default

        default = None

        if sys.platform == 'darwin':
            default = os.path.join(PYTHON_TESTS_PACKAGE_DIR, 'Terminal.sh')
            if not os.access(default, os.X_OK):
                os.chmod(default, 0755)
        else:
            ps = 'ps -eo comm | grep -E "gnome-session|ksmserver|' + \
                'xfce4-session" | grep -v grep'
            wm = [x.replace("\n", '') for x in os.popen(ps)]
            if wm:
                if wm[0] == 'gnome-session':
                    default = 'gnome-terminal'
                elif wm[0] == 'xfce4-session':
                    default = 'terminal'
                elif wm[0] == 'ksmserver':
                    default = 'konsole'
            if not default:
                default = 'xterm'

        TerminalSelector.default = default
        return default


test_modules = {
    'django': 'manage.py',
    'setup.py': 'setup.py'
}

test_commands = {
    'django': 'test',
    'nose': '',
    'setup.py': 'test -q'
}


class PythonTestCommandBase(sublime_plugin.TextCommand):

    def get_test_command(self, mode):
        default_test_module = test_modules.get(mode, None)
        default_test_command = test_commands.get(mode, None)

        test_cmd = self.view.settings().get(
            TEST_COMMAND_SETTING, default_test_command)
        test_module = self.view.settings().get(
            TEST_MODULE_SETTING, default_test_module)

        virtualenv = self.view.settings().get(VIRTUALENV_SETTING, None)

        # User can override this with a setting if necessary. Otherwise, we'll
        # try to discover the Python project's root directory.
        full_test_command = None

        if mode == 'nose':
            full_test_command = "nosetests"
        else:
            project_root = self.view.settings().get(PYTHON_PROJECT_ROOT_SETTING)

            if project_root is None:
                project_root = find_file(
                    ['settings.py', 'setup.py'],
                    os.path.dirname(self.view.file_name()))

            if project_root:
                full_test_command = 'python %s %s' % (
                    os.path.join(project_root, test_module), test_cmd)

        if virtualenv:
            full_test_command = 'venvwrapper && workon %s && %s' % (
                virtualenv, full_test_command)

        return full_test_command

    def run_shell_command(self, cmd):
        return subprocess.Popen(
            [cmd],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
        ).communicate()

    def run_test_command(self, test_cmd, test_name):
        terminal = self.view.settings().get(TEST_TERMINAL_SETTING, None)

        cmd = '"%s" "%s %s"' % (
            TerminalSelector.get(terminal), test_cmd, test_name)

        return self.run_shell_command(cmd)

    def _run(self, edit, target):
        mode = self.view.settings().get(TEST_MODE, 'django')
        test_command = self.get_test_command(mode)
        test_name = get_test_name(self.view, mode, target=target)
        output = self.run_test_command(test_command, test_name)
        print output


class RunPythonTestSuiteCommand(PythonTestCommandBase):
    def run(self, edit):
        self._run(edit, 'suite')


class RunPythonTestClassCommand(PythonTestCommandBase):
    def run(self, edit):
        self._run(edit, 'class')


class RunPythonTestMethodCommand(PythonTestCommandBase):
    def run(self, edit):
        self._run(edit, 'method')
