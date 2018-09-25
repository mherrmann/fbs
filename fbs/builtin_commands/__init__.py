"""
This module contains all of fbs's built-in commands. They are invoked when you
run `python -m fbs <command>` on the command line. But you are also free to
import them in your Python build script and execute them there.
"""

from fbs import path, SETTINGS
from fbs.cmdline import command
from fbs.platform import is_windows, is_mac, is_linux, is_arch_linux
from fbs.resources import copy_with_filtering
from os import listdir, remove, unlink, mkdir
from os.path import join, isfile, isdir, islink, dirname, exists
from shutil import rmtree
from unittest import TestSuite, TextTestRunner, defaultTestLoader

import os
import subprocess
import sys

@command
def startproject():
    """
    Start a new fbs project in the current directory
    """
    if exists('src'):
        print('The src/ directory already exists. Aborting.')
        return
    app_name = _prompt_for_nonempty_value('App name (eg. MyApp): ')
    author = _prompt_for_nonempty_value('App author (eg. Joe Developer): ')
    mac_bundle_identifier = _prompt_for_nonempty_value(
        'Mac bundle identifier (eg. com.joe.myapp): '
    )
    mkdir('src')
    template_dir = join(dirname(__file__), 'project_template')
    settings_file = lambda name: \
        join(template_dir, 'src', 'build', 'settings', name)
    copy_with_filtering(
        template_dir, '.', {
            'app_name': app_name,
            'author': author,
            'mac_bundle_identifier': mac_bundle_identifier
        },
        files_to_filter=[settings_file('base.json'), settings_file('mac.json')]
    )
    print(
        "\nCreated the src/ directory. If you have PyQt5 or PySide2\n"
        "installed, then you can now do:\n\n"
        "    python -m fbs run\n"
    )

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

def _prompt_for_nonempty_value(message):
    result = ''
    while not result:
        result = input(message)
    return result