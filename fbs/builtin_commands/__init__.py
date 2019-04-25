"""
This module contains all of fbs's built-in commands. They are invoked when you
run `fbs <command>` on the command line. But you are also free to import them in
your Python build script and execute them there.
"""
from fbs import path, SETTINGS, activate_profile
from fbs.builtin_commands._util import prompt_for_value, \
    require_existing_project, update_json
from fbs.cmdline import command
from fbs.resources import copy_with_filtering
from fbs.upload import _upload_repo
from fbs_runtime import FbsError
from fbs_runtime.platform import is_windows, is_mac, is_linux, is_arch_linux, \
    is_ubuntu, is_fedora
from getpass import getuser
from importlib.util import find_spec
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
    Start a new project in the current directory
    """
    if exists('src'):
        raise FbsError('The src/ directory already exists. Aborting.')
    app = prompt_for_value('App name', default='MyApp')
    while ' ' in app:
        print('Sorry, spaces in the app name are not yet supported.')
        app = prompt_for_value('App name', default='MyApp')
    user = getuser().title()
    author = prompt_for_value('Author', default=user)
    has_pyqt = _has_module('PyQt5')
    has_pyside = _has_module('PySide2')
    if has_pyqt and not has_pyside:
        python_bindings = 'PyQt5'
    elif not has_pyqt and has_pyside:
        python_bindings = 'PySide2'
    else:
        python_bindings = prompt_for_value(
            'Qt bindings', choices=('PyQt5', 'PySide2'), default='PyQt5'
        )
    eg_bundle_id = 'com.%s.%s' % (
        author.lower().split()[0], ''.join(app.lower().split())
    )
    mac_bundle_identifier = prompt_for_value(
        'Mac bundle identifier (eg. %s, optional)' % eg_bundle_id,
        optional=True
    )
    mkdir('src')
    template_dir = join(dirname(__file__), 'project_template')
    template_path = lambda relpath: join(template_dir, *relpath.split('/'))
    copy_with_filtering(
        template_dir, '.', {
            'app_name': app,
            'author': author,
            'mac_bundle_identifier': mac_bundle_identifier,
            'python_bindings': python_bindings
        },
        files_to_filter=[
            template_path('src/build/settings/base.json'),
            template_path('src/build/settings/mac.json'),
            template_path('src/main/python/main.py')
        ]
    )
    print('')
    _LOG.info(
        "Created the src/ directory. If you have %s installed, you can now "
        "do:\n\n    fbs run", python_bindings
    )

@command
def run():
    """
    Run your app from source
    """
    require_existing_project()
    if not _has_module('PyQt5') and not _has_module('PySide2'):
        raise FbsError(
            "Couldn't find PyQt5 or PySide2. Maybe you need to:\n"
            "    pip install PyQt5==5.9.2 or\n"
            "    pip install PySide2==5.12.2"
        )
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
    Compile your code to a standalone executable
    """
    require_existing_project()
    if not _has_module('PyInstaller'):
        raise FbsError(
            "Could not find PyInstaller. Maybe you need to:\n"
            "    pip install PyInstaller==3.4"
        )
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
            raise FbsError('Unsupported OS')
    _LOG.info(
        "Done. You can now run `%s`. If that doesn't work, see "
        "https://build-system.fman.io/troubleshooting.", executable
    )

@command
def installer():
    """
    Create an installer for your app
    """
    require_existing_project()
    if not exists(path('${freeze_dir}')):
        raise FbsError(
            'It seems your app has not yet been frozen. Please run:\n'
            '    fbs freeze'
        )
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
            raise FbsError('Unsupported Linux distribution')
        msg_parts.append(
            'You can for instance install it via the following command:\n'
            '    %s\n'
            'This places it in /opt/%s. To uninstall it again, you can use:\n'
            '    %s'
            % (install_cmd, app_name, remove_cmd)
        )
    else:
        raise FbsError('Unsupported OS')
    _LOG.info(' '.join(msg_parts))

@command
def sign_installer():
    """
    Sign installer, so the user's OS trusts it
    """
    require_existing_project()
    if is_arch_linux():
        from fbs.sign_installer.arch import sign_installer_arch
        sign_installer_arch()
    elif is_fedora():
        from fbs.sign_installer.fedora import sign_installer_fedora
        sign_installer_fedora()
    else:
        _LOG.info('This command is not (yet) supported on this platform.')

@command
def repo():
    """
    Generate files for automatic updates
    """
    require_existing_project()
    app_name = SETTINGS['app_name']
    pkg_name = app_name.lower()
    try:
        gpg_key = SETTINGS['gpg_key']
    except KeyError:
        raise FbsError(
            'GPG key for code signing is not configured. You might want to '
            'either\n'
            '    1) run `fbs gengpgkey` or\n'
            '    2) set "gpg_key" and "gpg_pass" in src/build/settings/.'
        )
    if is_ubuntu():
        from fbs.repo.ubuntu import create_repo_ubuntu
        if not SETTINGS['description']:
            _LOG.info(
                'Hint: Your app\'s "description" is empty. Consider setting it '
                'in src/build/settings/linux.json.'
            )
        create_repo_ubuntu()
        _LOG.info(
            'Done. You can test the repository with the following commands:\n'
            '    echo "deb [arch=amd64] file://%s stable main" '
                '| sudo tee /etc/apt/sources.list.d/%s.list\n'
            '    sudo apt-key add %s\n'
            '    sudo apt-get update\n'
            '    sudo apt-get install %s\n'
            'To revert these changes:\n'
            '    sudo dpkg --purge %s\n'
            '    sudo apt-key del %s\n'
            '    sudo rm /etc/apt/sources.list.d/%s.list\n'
            '    sudo apt-get update',
            path('target/repo'), pkg_name,
            path('src/sign/linux/public-key.gpg'), pkg_name, pkg_name, gpg_key,
            pkg_name,
            extra={'wrap': False}
        )
    elif is_arch_linux():
        from fbs.repo.arch import create_repo_arch
        create_repo_arch()
        _LOG.info(
            "Done. You can test the repository with the following commands:\n"
            "    sudo cp /etc/pacman.conf /etc/pacman.conf.bu\n"
            "    echo -e '\\n[%s]\\nServer = file://%s' "
                "| sudo tee -a /etc/pacman.conf\n"
            "    sudo pacman-key --add %s\n"
            "    sudo pacman-key --lsign-key %s\n"
            "    sudo pacman -Syu %s\n"
            "To revert these changes:\n"
            "    sudo pacman -R %s\n"
            "    sudo pacman-key --delete %s\n"
            "    sudo mv /etc/pacman.conf.bu /etc/pacman.conf",
            app_name, path('target/repo'),
            path('src/sign/linux/public-key.gpg'), gpg_key, pkg_name, pkg_name,
            gpg_key,
            extra={'wrap': False}
        )
    elif is_fedora():
        from fbs.repo.fedora import create_repo_fedora
        create_repo_fedora()
        _LOG.info(
            "Done. You can test the repository with the following commands:\n"
            "    sudo rpm -v --import %s\n"
            "    sudo dnf config-manager --add-repo file://%s/target/repo\n"
            "    sudo dnf install %s\n"
            "To revert these changes:\n"
            "    sudo dnf remove %s\n"
            "    sudo rm /etc/yum.repos.d/*%s*.repo\n"
            "    sudo rpm --erase gpg-pubkey-%s",
            path('src/sign/linux/public-key.gpg'), SETTINGS['project_dir'],
            pkg_name, pkg_name, app_name, gpg_key[-8:].lower(),
            extra={'wrap': False}
        )
    else:
        raise FbsError('This command is not supported on this platform.')

@command
def upload():
    """
    Upload installer and repository to fbs.sh
    """
    require_existing_project()
    try:
        username = SETTINGS['fbs_user']
        password = SETTINGS['fbs_pass']
    except KeyError as e:
        raise FbsError(
            'Could not find setting "%s". You may want to invoke one of the '
            'following:\n'
            ' * fbs register\n'
            ' * fbs login'
            % (e.args[0],)
        ) from None
    _upload_repo(username, password)
    app_name = SETTINGS['app_name']
    url = lambda p: 'https://fbs.sh/%s/%s/%s' % (username, app_name, p)
    message = 'Done! '
    pkg_name = app_name.lower()
    installer_url = url(SETTINGS['installer'])
    if is_linux():
        message += 'Your users can now install your app via the following ' \
                   'commands:\n'
        format_commands = lambda *cmds: '\n'.join('    ' + c for c in cmds)
        repo_url = url(SETTINGS['repo_subdir'])
        if is_ubuntu():
            message += format_commands(
                "sudo apt-get install apt-transport-https",
                "wget -qO - %s | sudo apt-key add -" % url('public-key.gpg'),
                "echo 'deb [arch=amd64] %s stable main' | " % repo_url +
                "sudo tee /etc/apt/sources.list.d/%s.list" % pkg_name,
                "sudo apt-get update",
                "sudo apt-get install " + pkg_name
            )
            message += '\nIf they already have your app installed, they can ' \
                       'force an immediate update via:\n'
            message += format_commands(
                'sudo apt-get update '
                '-o Dir::Etc::sourcelist="/etc/apt/sources.list.d/%s.list" '
                '-o Dir::Etc::sourceparts="-" -o APT::Get::List-Cleanup="0"'
                % pkg_name,
                'sudo apt-get install --only-upgrade ' + pkg_name
            )
        elif is_arch_linux():
            message += format_commands(
                "curl -O %s && " % url('public-key.gpg') +
                "sudo pacman-key --add public-key.gpg && " +
                "sudo pacman-key --lsign-key %s && " % SETTINGS['gpg_key'] +
                "rm public-key.gpg",
                "echo -e '\\n[%s]\\nServer = %s' | sudo tee -a /etc/pacman.conf"
                % (app_name, repo_url),
                "sudo pacman -Syu " + pkg_name
            )
            message += '\nIf they already have your app installed, they can ' \
                       'force an immediate update via:\n'
            message += format_commands('sudo pacman -Syu --needed ' + pkg_name)
        elif is_fedora():
            message += format_commands(
                "sudo rpm -v --import " + url('public-key.gpg'),
                "sudo dnf config-manager --add-repo %s/%s.repo"
                % (repo_url, app_name),
                "sudo dnf install " + pkg_name
            )
            message += "\n(On CentOS, replace 'dnf' by 'yum' and " \
                       "'dnf config-manager' by 'yum-config-manager'.)"
            message += '\nIf they already have your app installed, they can ' \
                       'force an immediate update via:\n'
            message += \
                format_commands('sudo dnf upgrade %s --refresh' % pkg_name)
            message += '\nThis is for Fedora. For CentOS, use:\n'
            message += format_commands(
                'sudo yum clean all && sudo yum upgrade ' + pkg_name
            )
        else:
            raise FbsError('This Linux distribution is not supported.')
        message += '\nFinally, your users can also install without automatic ' \
                   'updates by downloading:\n    ' + installer_url
        extra = {'wrap': False}
    else:
        message += 'Your users can now download and install %s.' % installer_url
        extra = None
    _LOG.info(message, extra=extra)

@command
def release():
    """
    Bump version and run clean,freeze,...,upload
    """
    require_existing_project()
    version = SETTINGS['version']
    next_version = _get_next_version(version)
    release_version = prompt_for_value('Release version', default=next_version)
    activate_profile('release')
    SETTINGS['version'] = release_version
    log_level = _LOG.level
    if log_level == logging.NOTSET:
        _LOG.setLevel(logging.WARNING)
    try:
        clean()
        freeze()
        installer()
        sign_installer()
        repo()
    finally:
        _LOG.setLevel(log_level)
    upload()
    base_json = 'src/build/settings/base.json'
    update_json(path(base_json), { 'version': release_version })
    _LOG.info('Also, %s was updated with the new version.', base_json)

@command
def test():
    """
    Execute your automated tests
    """
    require_existing_project()
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

def _has_module(name):
    return bool(find_spec(name))

def _get_next_version(version):
    version_parts = version.split('.')
    next_patch = str(int(version_parts[-1]) + 1)
    return '.'.join(version_parts[:-1]) + '.' + next_patch