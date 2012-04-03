# run_django_tests: Run the Django test the cursor resides within in an external
# terminal emulator.
#
# This code is licensed under the MIT license and copyright (c) Andrew Brookins
# <a.m.brookins@gmail.com>.
#
# The `TerminalSelector` class was extracted from the Sublime Terminal plugin
# and modified slightly. All of Sublime Terminal is licensed under the MIT
# license and copyright (c) 2011 Will Bond <will@wbond.net>

import os
import sublime
import sublime_plugin
import subprocess
import sys


DJANGO_PROJECT_ROOT_SETTING = 'django_project_root'
TEST_COMMAND_SETTING = 'django_test_command'
TEST_MODULE_SETTING = 'django_test_module'
TEST_TERMINAL_SETTING = 'django_test_terminal'
VIRTUALENV_SETTING = 'django_virtualenv'


def find_file(filename, starting_dir):
    """
    Recursively check the current and then parent directory for `filename`,
    starting from `starting_dir`.

    Returns the directory containing `filename` or None if not found.
    """
    exists = os.path.exists(os.path.join(starting_dir, filename))

    if exists:
        return starting_dir
    elif starting_dir == os.path.sep:
        # Stop if `starting_dir` is the root directory, identified on UNIX/Linux
        # systems as '/'
        return None
    else:
        return find_file(filename, os.path.dirname(starting_dir))


def get_current_code_entity(view, entity_selector):
    sel = view.sel()[0]
    entities = view.find_by_selector(entity_selector)
    current_entity = None

    for e in reversed(entities):
        if e.a < sel.a:
            current_entity = view.substr(e)
            break

    return current_entity


def get_test_name(view, include_method=True):
    test_cls = get_current_code_entity(view, 'entity.name.type.class')
    test_fn = get_current_code_entity(view, 'entity.name.function')
    app_name = find_file('models.py', view.file_name())
    test_name = None
    print include_method

    # Possibly the app keeps models in a models/ directory.
    if app_name is None:
        app_name = find_file('models', view.file_name())

    # The path is, e.g., /one/two/three/app_name, so get `app_name`.
    if app_name:
        app_name = app_name.split(os.path.sep)[-1]

    # Test functions must start with `test_`.
    # TODO: Make this configurable.
    if test_fn.startswith('test_') is False:
        return

    if include_method and test_fn and app_name:
        test_name = '%s.%s.%s' % (app_name, test_cls, test_fn)
    elif app_name and test_fn:
        test_name = '%s.%s' % (app_name, test_cls)

    return test_name


class NotFoundError(Exception):
    pass


class TerminalSelector(object):
    default = None

    @staticmethod
    def get(terminal=None):
        package_dir = os.path.join(sublime.packages_path(), __name__)

        if terminal:
            dir, executable = os.path.split(terminal)
            if not dir:
                joined_terminal = os.path.join(package_dir, executable)
                if os.path.exists(joined_terminal):
                    terminal = joined_terminal
                    if not os.access(terminal, os.X_OK):
                        os.chmod(terminal, 0755)
            return terminal

        if TerminalSelector.default:
            return TerminalSelector.default

        default = None

        if sys.platform == 'darwin':
            default = os.path.join(package_dir, 'Terminal.sh')
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


class DjangoTestCommandBase(sublime_plugin.TextCommand):

    def get_test_command(self):
        test_cmd = self.view.settings().get(TEST_COMMAND_SETTING, 'test')
        test_module = self.view.settings().get(TEST_MODULE_SETTING, 'manage.py')
        virtualenv = self.view.settings().get(VIRTUALENV_SETTING, None)
        # User can override this with a setting if necessary. Otherwise, we'll
        # try to discover the Django project's root directory.
        project_root = self.view.settings().get(DJANGO_PROJECT_ROOT_SETTING)
        full_test_command = None

        if project_root is None:
            project_root = find_file(
                'settings.py', os.path.dirname(self.view.file_name()))

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

    def run_test_command(self, test_cmd, include_method=False):
        test_name = get_test_name(self.view, include_method)
        terminal = self.view.settings().get(TEST_TERMINAL_SETTING, None)

        if test_name is None:
            return

        cmd = '"%s" "%s %s"' % (
            TerminalSelector.get(terminal), test_cmd, test_name)

        return self.run_shell_command(cmd)


class RunDjangoTestSuiteCommand(DjangoTestCommandBase):
    def run(self, edit):
        test_command = self.get_test_command()
        output = self.run_test_command(test_command, include_method=False)
        print output[0]


class RunDjangoTestMethodCommand(DjangoTestCommandBase):
    def run(self, edit):
        test_command = self.get_test_command()
        output = self.run_test_command(test_command, include_method=True)
        print output[0]
