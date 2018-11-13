"""
This module contains all of fbs's built-in commands. They are invoked when you
run `python -m fbs <command>` on the command line. But you are also free to
import them in your Python build script and execute them there.
"""
from fbs import path, SETTINGS
from fbs.cmdline import command
from fbs.resources import copy_with_filtering
from fbs_runtime.platform import is_windows, is_mac, is_linux, is_arch_linux, \
    is_ubuntu, is_fedora
from getpass import getuser
from os import listdir, remove, unlink, mkdir
from os.path import join, isfile, isdir, islink, dirname, exists
from shutil import rmtree
from unittest import TestSuite, TextTestRunner, defaultTestLoader

import logging
import os
import subprocess
import sys

_LOG = logging.getLogger(__name__)

@command
def startproject():
    """
    Start a new fbs project in the current directory
    """
    if exists('src'):
        _LOG.warning('The src/ directory already exists. Aborting.')
        return
    try:
        app = _prompt_for_value('App name [MyApp] : ', default='MyApp')
        user = getuser().title()
        author = _prompt_for_value('Author [%s] : ' % user, default=user)
        version = \
            _prompt_for_value('Initial version [0.0.1] : ', default='0.0.1')
        eg_bundle_id = 'com.%s.%s' % (
            author.lower().split()[0], ''.join(app.lower().split())
        )
        mac_bundle_identifier = _prompt_for_value(
            'Mac bundle identifier (eg. %s, optional) : ' % eg_bundle_id,
            optional=True
        )
    except KeyboardInterrupt:
        print('')
        return
    print('')
    mkdir('src')
    template_dir = join(dirname(__file__), 'project_template')
    pth = lambda relpath: join(template_dir, *relpath.split('/'))
    python_bindings = _get_python_bindings()
    copy_with_filtering(
        template_dir, '.', {
            'app_name': app,
            'author': author,
            'version': version,
            'mac_bundle_identifier': mac_bundle_identifier,
            'python_bindings': python_bindings
        },
        files_to_filter=[
            pth('src/build/settings/base.json'),
            pth('src/build/settings/mac.json'),
            pth('src/main/python/main.py')
        ]
    )
    _LOG.info(
        "Created the src/ directory. If you have %s installed, you can now "
        "do:\n    python -m fbs run", python_bindings
    )

def _get_python_bindings():
    # Use PyQt5 by default. Only use PySide2 if it is available and PyQt5 isn't.
    try:
        import PySide2
    except ImportError:
        pass
    else:
        try:
            import PyQt5
        except ImportError:
            return 'PySide2'
    return 'PyQt5'

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
    subprocess.run([sys.executable, path(SETTINGS['main_module'])], env=env)

@command
def freeze(debug=False):
    """
    Compile your application to a standalone executable
    """
    # Import respective functions late to avoid circular import
    # fbs <-> fbs.freeze.X.
    app_name = SETTINGS['app_name']
    if is_mac():
        from fbs.freeze.mac import freeze_mac
        freeze_mac(debug=debug)
        executable = 'target/%s.app/Contents/MacOS/%s' % (app_name, app_name)
    else:
        executable = join('target', app_name, app_name)
        if is_windows():
            from fbs.freeze.windows import freeze_windows
            freeze_windows(debug=debug)
            executable += '.exe'
        elif is_linux():
            if is_ubuntu():
                from fbs.freeze.ubuntu import freeze_ubuntu
                freeze_ubuntu(debug=debug)
            elif is_arch_linux():
                from fbs.freeze.arch import freeze_arch
                freeze_arch(debug=debug)
            elif is_fedora():
                from fbs.freeze.fedora import freeze_fedora
                freeze_fedora(debug=debug)
            else:
                from fbs.freeze.linux import freeze_linux
                freeze_linux(debug=debug)
        else:
            raise RuntimeError('Unsupported OS')
    _LOG.info(
        "Done. You can now run `%s`. If that doesn't work, see "
        "https://build-system.fman.io/troubleshooting.", executable
    )

@command
def installer():
    """
    Create an installer for your app
    """
    out_file = join('target', SETTINGS['installer'])
    msg_parts = ['Created %s.' % out_file]
    if is_windows():
        from fbs.installer.windows import create_installer_windows
        create_installer_windows()
    elif is_mac():
        from fbs.installer.mac import create_installer_mac
        create_installer_mac()
    elif is_linux():
        app_name = SETTINGS['app_name']
        if is_ubuntu():
            from fbs.installer.ubuntu import create_installer_ubuntu
            create_installer_ubuntu()
            install_cmd = 'sudo dpkg -i ' + out_file
            remove_cmd = 'sudo dpkg --purge ' + app_name
        elif is_arch_linux():
            from fbs.installer.arch import create_installer_arch
            create_installer_arch()
            install_cmd = 'sudo pacman -U ' + out_file
            remove_cmd = 'sudo pacman -R ' + app_name
        elif is_fedora():
            from fbs.installer.fedora import create_installer_fedora
            create_installer_fedora()
            install_cmd = 'sudo dnf install ' + out_file
            remove_cmd = 'sudo dnf remove ' + app_name
        else:
            raise RuntimeError('Unsupported Linux distribution')
        msg_parts.append(
            'You can for instance install it via the following command:\n'
            '    %s\n'
            'This places it in /opt/%s. To uninstall it again, you can use:\n'
            '    %s'
            % (install_cmd, app_name, remove_cmd)
        )
    else:
        raise RuntimeError('Unsupported OS')
    _LOG.info(' '.join(msg_parts))

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
        _LOG.warning(
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

def _prompt_for_value(message, optional=False, default=''):
    result = input(message).strip()
    if not result and default:
        print(default)
        return default
    if not optional:
        while not result:
            result = input(message).strip()
    return result