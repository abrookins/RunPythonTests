import os
import sublime
import sublime_plugin
import subprocess
from terminal_selector import TerminalSelector


DJANGO_PROJECT_ROOT_SETTINGS = 'django_project_root'
TEST_COMMAND_SETTING = 'django_test_command'
TEST_MODULE_SETTING = 'django_test_module'
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


def get_test_name(view, app_name, include_method=True):
    test_cls = get_current_code_entity(view, 'entity.name.type.class')
    test_fn = get_current_code_entity(view, 'entity.name.function')
    app_name = find_file('models.py', view.file_name())
    test_name = None

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


class DjangoTestCommandBase(sublime_plugin.TextCommand):

    def get_test_command(self):
        test_cmd = self.view.settings().get(TEST_COMMAND_SETTING, 'test')
        test_module = self.view.settings().get(TEST_MODULE_SETTING, 'manage.py')
        virtualenv = self.view.settings().get(VIRTUALENV_SETTING, None)
        # User can override this with a setting if necessary. Otherwise, we'll
        # try to discover the Django project's root directory.
        project_root = self.view.settings().get(DJANGO_PROJECT_ROOT_SETTINGS)
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
        package_dir = os.path.join(sublime.packages_path(), __name__)

        if test_name is None:
            return

        cmd = '"%s" "%s %s"' % (
            TerminalSelector.get(package_dir), test_cmd, test_name)

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
