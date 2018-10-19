from fbs import path, SETTINGS
from fbs._state import LOADED_PROFILES
from fbs.resources import copy_with_filtering, get_icons
from os import makedirs, remove
from os.path import join, dirname, exists
from shutil import copy, rmtree, copytree
from subprocess import run

def generate_installer_files():
    if exists(path('target/installer')):
        rmtree(path('target/installer'))
    copytree(path('${freeze_dir}'), path('target/installer/opt/${app_name}'))
    _generate_global_resources()
    _generate_icons()

def run_fpm(output_type):
    dest = path('target/${installer}')
    if exists(dest):
        remove(dest)
    # Lower-case the name to avoid the following fpm warning:
    #  > Debian tools (dpkg/apt) don't do well with packages that use capital
    #  > letters in the name. In some cases it will automatically downcase
    #  > them, in others it will not. It is confusing. Best to not use any
    #  > capital letters at all.
    name = SETTINGS['app_name'].lower()
    args = [
        'fpm', '-s', 'dir',
        # We set the log level to error because fpm prints the following warning
        # even if we don't have anything in /etc:
        #  > Debian packaging tools generally labels all files in /etc as config
        #  > files, as mandated by policy, so fpm defaults to this behavior for
        #  > deb packages. You can disable this default behavior with
        #  > --deb-no-default-config-files flag
        '--log', 'error',
        '-C', path('target/installer'),
        '-n', name,
        '-v', SETTINGS['version'],
        '--vendor', SETTINGS['author'],
        '-t', output_type,
        '-p', dest
    ]
    try:
        run(args, check=True)
    except FileNotFoundError:
        raise FileNotFoundError(
            "fbs could not find executable 'fpm'. Please install fpm using the "
            "instructions at "
            "https://fpm.readthedocs.io/en/latest/installing.html."
        ) from None

def _generate_global_resources():
    for profile in LOADED_PROFILES:
        source_dir = 'src/main/resources/%s-global' % profile
        copy_with_filtering(
            path(source_dir), path('target/installer'),
            files_to_filter=SETTINGS['resources_to_filter']
        )

def _generate_icons():
    dest_root = path('target/installer/usr/share/icons/hicolor')
    makedirs(dest_root)
    icons_fname = '%s.png' % SETTINGS['app_name']
    for size, icon_path in get_icons():
        icon_dest = join(dest_root, '%dx%d' % (size, size), 'apps', icons_fname)
        makedirs(dirname(icon_dest))
        copy(icon_path, icon_dest)