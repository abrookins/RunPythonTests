"""
run_python_tests.py: Run the Python test nearest to the cursor.

The test is launched in an external shell, such as iTerm, Terminal.app or
Konsole.

This code is licensed under the MIT license and copyright (c) Andrew Brookins
<a.m.brookins@gmail.com>.
"""
import settings
import sublime_plugin
import util


class PythonTestCommandBase(sublime_plugin.TextCommand):
    def _run(self, edit, target):
        mode = self.view.settings().get(settings.TEST_MODE, 'django')
        terminal = self.view.settings().get(settings.TEST_TERMINAL_SETTING, None)
        test_command = util.get_test_command(
            mode, self.view.settings(), self.view.file_name())
        test_name = util.get_test_name(self.view, mode, target=target)
        util.run_test_command(test_command, test_name, terminal)


class RunPythonTestSuiteCommand(PythonTestCommandBase):
    def run(self, edit):
        self._run(edit, 'suite')


class RunPythonTestClassCommand(PythonTestCommandBase):
    def run(self, edit):
        self._run(edit, 'class')


class RunPythonTestMethodCommand(PythonTestCommandBase):
    def run(self, edit):
        self._run(edit, 'method')
