# This code was copied from the Sublime Terminal plugin and modified slightly.
# All of Sublime Terminal is licensed under the MIT license.
# Copyright (c) 2011 Will Bond <will@wbond.net>

import sublime
import os
import sys


class NotFoundError(Exception):
    pass


class TerminalSelector():
    default = None

    @staticmethod
    def get(package_dir):
        settings = sublime.load_settings('RunDjangoTests.sublime-settings')
        terminal = settings.get('django_test_terminal')

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
