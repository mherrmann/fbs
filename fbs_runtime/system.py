import os
import sys

def is_windows():
    """
    Return True if the current OS is Windows, False otherwise.
    """
    return sys.platform in ('win32', 'cygwin')

def is_mac():
    """
    Return True if the current OS is macOS, False otherwise.
    """
    return sys.platform == 'darwin'

def is_linux():
    """
    Return True if the current OS is Linux, False otherwise.
    """
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
    curr_desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
    return curr_desktop in ('unity', 'gnome', 'x-cinnamon')

def is_kde_based():
    curr_desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
    if curr_desktop == 'kde':
        return True
    gdmsession = os.environ.get('GDMSESSION', '').lower()
    return gdmsession.startswith('kde')