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
    """
    Returns 'Windows', 'Mac' or 'Linux', depending on the current OS. If the OS
    can't be determined, a RuntimeError is raised.
    """
    if is_windows():
        return 'Windows'
    if is_mac():
        return 'Mac'
    if is_linux():
        return 'Linux'
    raise RuntimeError('Unknown operating system.')

def is_ubuntu():
    try:
        return _get_os_release_name().startswith('Ubuntu')
    except FileNotFoundError:
        return False

def is_arch_linux():
    try:
        return _get_os_release_name().startswith('Arch Linux')
    except FileNotFoundError:
        return False

def is_fedora():
    try:
        return _get_os_release_name().startswith('Fedora')
    except FileNotFoundError:
        return False

def is_gnome_based():
    curr_desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
    return curr_desktop in ('unity', 'gnome', 'x-cinnamon')

def is_kde_based():
    curr_desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
    if curr_desktop == 'kde':
        return True
    gdmsession = os.environ.get('GDMSESSION', '').lower()
    return gdmsession.startswith('kde')

def _get_os_release_name():
    with open('/etc/os-release', 'r') as f:
        for line in f:
            line = line.rstrip()
            if line.startswith('NAME='):
                name = line[len('NAME='):]
                return name.strip('"')