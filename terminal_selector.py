"""
terminal_selector.py: Detect a proper external terminal for the current OS.

The `TerminalSelector` class was extracted from the Sublime Terminal plugin
and modified slightly. All of Sublime Terminal is licensed under the MIT
license and copyright (c) 2011 Will Bond <will@wbond.net>
"""
import os
import settings
import sys


class TerminalSelector(object):
    default = None

    @staticmethod
    def get(terminal=None):
        if terminal:
            dir, executable = os.path.split(terminal)
            if not dir:
                joined_terminal = os.path.join(
                    settings.PYTHON_TESTS_PACKAGE_DIR, executable)
                if os.path.exists(joined_terminal):
                    terminal = joined_terminal
                    if not os.access(terminal, os.X_OK):
                        os.chmod(terminal, 0755)
            return terminal

        if TerminalSelector.default:
            return TerminalSelector.default

        default = None

        if sys.platform == 'darwin':
            default = os.path.join(
                settings.PYTHON_TESTS_PACKAGE_DIR, 'Terminal.sh')
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
