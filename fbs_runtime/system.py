import os
import sys

def is_windows():
    return sys.platform in ('win32', 'cygwin')

def is_mac():
    return sys.platform == 'darwin'

def is_linux():
    return sys.platform.startswith('linux')

def name():
    if is_windows():
        return 'Windows'
    if is_mac():
        return 'Mac'
    if is_linux():
        return 'Linux'
    raise RuntimeError('Unknown operating system.')

def is_gnome_based():
    # If you update this, also update the same fn in the Core module!
    curr_desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
    return curr_desktop in ('unity', 'gnome', 'x-cinnamon')

def is_kde_based():
    # If you update this, also update the same fn in the Core module!
    curr_desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
    if curr_desktop == 'kde':
        return True
    gdmsession = os.environ.get('GDMSESSION', '').lower()
    return gdmsession.startswith('kde')