# RunDjangoTests

This is a plugin for Sublime Text 2.

The plugin provides commands to run a Django test method or suite (a test class)
from within a test file (by default, the commands are: Control-z, Control-t and
Control-z, Control-T, respectively)

You can customize it with the following settings (most helpful when added to a
project settings file, so you can customize per-project):

- "django_virtualenv": "< name of your virtualenv>"
- "django_test_module": "< name of your test module, if you aren't using `manage.py` (the default)"
- "django_test_command": "< name of the test command the module should run; defaults to `test` for `manage.py test`, set to an empty string if none is needed for your test module >"
