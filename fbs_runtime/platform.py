from fbs_runtime import _state

import os
import sys

def is_windows():
    """
    Return True if the current OS is Windows, False otherwise.
    """
    return name() == 'Windows'

def is_mac():
    """
    Return True if the current OS is macOS, False otherwise.
    """
    return name() == 'Mac'

def is_linux():
    """
    Return True if the current OS is Linux, False otherwise.
    """
    return name() == 'Linux'

def name():
    """
    Returns 'Windows', 'Mac' or 'Linux', depending on the current OS. If the OS
    can't be determined, a RuntimeError is raised.
    """
    if _state.PLATFORM_NAME is None:
        _state.PLATFORM_NAME = _get_name()
    return _state.PLATFORM_NAME

def _get_name():
    if sys.platform in ('win32', 'cygwin'):
        return 'Windows'
    if sys.platform == 'darwin':
        return 'Mac'
    if sys.platform.startswith('linux'):
        return 'Linux'
    raise RuntimeError('Unknown operating system.')

def is_ubuntu():
    try:
        return linux_distribution() == 'Ubuntu'
    except FileNotFoundError:
        return False

def is_arch_linux():
    try:
        return linux_distribution() == 'Arch'
    except FileNotFoundError:
        return False

def is_fedora():
    try:
        return linux_distribution() == 'Fedora'
    except FileNotFoundError:
        return False

def linux_distribution():
    if _state.LINUX_DISTRIBUTION is None:
        _state.LINUX_DISTRIBUTION = _get_linux_distribution()
    return _state.LINUX_DISTRIBUTION

def _get_linux_distribution():
    if not is_linux():
        return ''
    try:
        os_release = _get_os_release_name()
    except OSError:
        pass
    else:
        if os_release:
            return os_release.split(maxsplit=1)[0]
    return '<unknown>'

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