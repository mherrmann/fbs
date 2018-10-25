from fbs.freeze.linux import freeze_linux

def freeze_arch(extra_pyinstaller_args=None, debug=False):
    freeze_linux(extra_pyinstaller_args, debug)