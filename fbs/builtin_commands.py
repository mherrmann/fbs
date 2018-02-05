from fbs import path, SETTINGS
from fbs.cmdline import command
from fbs.platform import is_windows, is_mac, is_linux, is_arch_linux
from os import listdir, remove, unlink
from os.path import join, isfile, isdir, islink
from shutil import rmtree
from unittest import TestSuite, TextTestRunner, defaultTestLoader

import os
import subprocess
import sys

@command
def run():
    """
    Run your app from source
    """
    env = dict(os.environ)
    pythonpath = path('src/main/python')
    old_pythonpath = env.get('PYTHONPATH', '')
    if old_pythonpath:
        pythonpath += os.pathsep + old_pythonpath
    env['PYTHONPATH'] = pythonpath
    subprocess.run([sys.executable, SETTINGS['main_module']], env=env)

@command
def freeze():
    """
    Compile your application to a standalone executable
    """
    # Import respective functions late to avoid circular import
    # fbs <-> fbs.freeze.X:
    if is_windows():
        from fbs.freeze.windows import freeze_windows
        freeze_windows()
    elif is_mac():
        from fbs.freeze.mac import freeze_mac
        freeze_mac()
    elif is_linux():
        if is_arch_linux():
            from fbs.freeze.arch import freeze_arch
            freeze_arch()
        else:
            from fbs.freeze.linux import freeze_linux
            freeze_linux()
    else:
        raise RuntimeError('Unsupported OS')

@command
def installer():
    """
    Create an installer for your app
    """
    if is_windows():
        from fbs.installer.windows import create_installer_windows
        create_installer_windows()
    elif is_mac():
        from fbs.installer.mac import create_installer_mac
        create_installer_mac()
    else:
        raise RuntimeError('Unsupported OS')

@command
def test():
    """
    Execute your automated tests
    """
    sys.path.append(path('src/main/python'))
    suite = TestSuite()
    test_dirs = SETTINGS['test_dirs']
    for test_dir in map(path, test_dirs):
        sys.path.append(test_dir)
        try:
            dir_names = listdir(test_dir)
        except FileNotFoundError:
            continue
        for dir_name in dir_names:
            dir_path = join(test_dir, dir_name)
            if isfile(join(dir_path, '__init__.py')):
                suite.addTest(defaultTestLoader.discover(
                    dir_name, top_level_dir=test_dir
                ))
    has_tests = bool(list(suite))
    if has_tests:
        TextTestRunner().run(suite)
    else:
        print(
            'No tests found. You can add them to:\n * '+
            '\n * '.join(test_dirs)
        )

@command
def clean():
    """
    Remove previous build outputs
    """
    try:
        rmtree(path('target'))
    except FileNotFoundError:
        return
    except OSError:
        # In a docker container, target/ may be mounted so we can't delete it.
        # Delete its contents instead:
        for f in listdir(path('target')):
            fpath = join(path('target'), f)
            if isdir(fpath):
                rmtree(fpath, ignore_errors=True)
            elif isfile(fpath):
                remove(fpath)
            elif islink(fpath):
                unlink(fpath)