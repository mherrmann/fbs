# Make is_windows, is_mac, is_linux available here as well:
from fbs_runtime.system import is_windows, is_mac, is_linux, name

def is_ubuntu():
    with open('/etc/issue', 'r') as f:
        return f.read().startswith('Ubuntu ')

def is_arch_linux():
    with open('/etc/issue', 'r') as f:
        return f.read().startswith('Arch Linux ')