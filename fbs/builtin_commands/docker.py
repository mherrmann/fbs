from fbs import path, SETTINGS, _defaults
from fbs.cmdline import command
from fbs.resources import _copy
from fbs_runtime import FbsError
from gitignore_parser import parse_gitignore
from os import listdir
from os.path import exists
from shutil import rmtree
from subprocess import run

import logging

__all__ = ['build_vm', 'run_vm']

_LOG = logging.getLogger(__name__)

@command
def build_vm(name):
    """
    Build a virtual machine. Eg.: build_vm ubuntu
    """
    build_dir = path('target/%s-docker-image' % name)
    if exists(build_dir):
        rmtree(build_dir)
    src_dir = 'src/build/docker/' + name
    src_dir_exists = False
    for path_fn in _defaults.path, path:
        src_dir_exists = _copy(path_fn, src_dir, build_dir) or src_dir_exists
    if not src_dir_exists:
        raise FbsError('Could not find %s. Aborting.' % src_dir)
    build_files = SETTINGS['docker_images'].get(name, {}).get('build_files', [])
    for path_fn in _defaults.path, path:
        for p in build_files:
            _copy(path_fn, p, build_dir)
    _run_docker(
        ['build', '--pull', '-t', _get_docker_id(name), build_dir], check=True
    )

@command
def run_vm(name):
    """
    Run a virtual machine. Eg.: run_vm ubuntu
    """
    args = ['run', '-it']
    for item in _get_docker_mounts(name).items():
        args.extend(['-v', '%s:%s' % item])
    args.append(_get_docker_id(name))
    _LOG.info(
        'You are now in a Docker container running %s. Use the normal commands '
        '`fbs freeze` etc. to build your app for this platform.',
        name.title()
    )
    _run_docker(args)

def _run_docker(args, check=False):
    try:
        run(['docker'] + args, check=check)
    except FileNotFoundError:
        raise FbsError(
            'fbs could not find Docker. Is it installed and on your PATH?'
        )

def _get_docker_id(name):
    prefix = SETTINGS['app_name'].replace(' ', '_').lower()
    suffix = name.lower()
    return prefix + '/' + suffix

def _get_docker_mounts(name):
    result = {'target/' + name.lower(): 'target'}
    gitignore = path('.gitignore')
    if not exists(gitignore):
        gitignore = _defaults.path('.gitignore')
    is_in_gitignore = parse_gitignore(gitignore)
    for file_name in listdir(path('.')):
        if is_in_gitignore(path(file_name)):
            continue
        result[file_name] = file_name
    path_in_docker = lambda p: '/root/%s/%s' % (SETTINGS['app_name'], p)
    return {path(src): path_in_docker(dest) for src, dest in result.items()}

def _get_settings(name):
    return SETTINGS['docker_images'][name]