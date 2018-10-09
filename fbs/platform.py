# Make is_windows, is_mac, is_linux available here as well:
from fbs_runtime.system import is_windows, is_mac, is_linux, name

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

def _get_os_release_name():
    with open('/etc/os-release', 'r') as f:
        for line in f:
            line = line.rstrip()
            if line.startswith('NAME='):
                name = line[len('NAME='):]
                return name.strip('"')