# RunPythonTests

This is a plugin for Sublime Text 2.

The plugin provides commands to run the current test method, class or package 
tests from within a test file. The nearest test for the given target (method, 
class or package, AKA "suite") above the cursor is chosen and launched in an
external shell.

## Requirements

There are a bit obvious, but:

- virtualenv and virtualenvwrapper are required for virtualenv support
- nose is required for "nose" mode
- Django is required for "django" mode

## Keyboard shortcuts

By default, the commands are:

- Run test function: Control-z, Control-t
- Run test class: Control-z, Control-T
- Run test suite: Control-z, Control-r

## Settings

The following setting is *required*:

- "python_project_root"

    The absolute path to the root directory of your project.

These settings are optional and work best inside of your project settings file:

- "python_test_mode"

    **Options**: "django", "nose" or "setup.py"

    Whether to use manage.py and django test format strings to run tests, nose's
    'nosetests' command and nose test format strings, or setup.py (default is
    django; note that only the suite command works in setup.py mode)

- "python_virtualenv"

    The name of a virtualenv to activate using virtualenvwrapper.

- "python_test_module"

    The name of a custom Python module to use for running tests. "manage.py" is
    the default when using django

- "python_test_command"

    The name of a custom command the test module should run. Defaults to `test`
    with Django, IE `manage.py test`.

- "python_test_terminal"

    **Options**: "iterm.sh", "terminal.sh", "gnome-terminal", "terminal",
    "konsole", "xterm"

    The name of the terminal app to run tests in. On OS X, use "iterm.sh" for
    iTerm 2 support or "terminal.sh" for Terminal.app. Otherwise the plugin will
    try to guess one of: gnome-terminal, terminal, konsole, or xterm.