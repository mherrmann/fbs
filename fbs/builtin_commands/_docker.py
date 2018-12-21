from fbs import path, SETTINGS
from fbs.builtin_commands import require_existing_project
from fbs.cmdline import command
from fbs.resources import _copy
from fbs_runtime import FbsError
from fbs_runtime._source import default_path
from os import listdir
from os.path import exists
from shutil import rmtree
from subprocess import run, CalledProcessError, PIPE

import logging

__all__ = ['buildvm', 'runvm']

_LOG = logging.getLogger(__name__)

@command
def buildvm(name):
    """
    Build a Linux VM. Eg.: buildvm ubuntu
    """
    require_existing_project()
    build_dir = path('target/%s-docker-image' % name)
    if exists(build_dir):
        rmtree(build_dir)
    src_root = 'src/build/docker'
    available_vms = set(listdir(default_path(src_root)))
    if exists(path(src_root)):
        available_vms.update(listdir(path(src_root)))
    if name not in available_vms:
        raise FbsError(
            'Could not find %s. Available VMs are:%s' %
            (name, ''.join(['\n * ' + vm for vm in available_vms]))
        )
    src_dir = src_root + '/' + name
    for path_fn in default_path, path:
        _copy(path_fn, src_dir, build_dir)
    settings = SETTINGS['docker_images'].get(name, {})
    for path_fn in default_path, path:
        for p in settings.get('build_files', []):
            _copy(path_fn, p, build_dir)
    args = ['build', '--pull', '-t', _get_docker_id(name), build_dir]
    for arg, value in settings.get('build_args', {}).items():
        args.extend(['--build-arg', '%s=%s' % (arg, value)])
    try:
        _run_docker(
            args, check=True, stdout=PIPE, stderr=PIPE,
            universal_newlines=True
        )
    except CalledProcessError as e:
        if '/private-key.gpg: no such file or directory' in e.stderr:
            message = 'Could not find private-key.gpg. Maybe you want to ' \
                      'run:\n    fbs gengpgkey'
        else:
            message = e.stdout + '\n' + e.stderr
        raise FbsError(message)
    _LOG.info('Done. You can now execute:\n    fbs runvm ' + name)

@command
def runvm(name):
    """
    Run a Linux VM. Eg.: runvm ubuntu
    """
    args = ['run', '-it']
    for item in _get_docker_mounts(name).items():
        args.extend(['-v', '%s:%s' % item])
    docker_id = _get_docker_id(name)
    args.append(docker_id)
    try:
        _run_docker(args, stderr=PIPE, universal_newlines=True, check=True)
    except CalledProcessError as e:
        if 'Unable to find image' in e.stderr:
            raise FbsError(
                'Docker could not find image %s. You may want to run:\n'
                '    fbs buildvm %s' % (docker_id, name)
            )

def _run_docker(args, **kwargs):
    try:
        return run(['docker'] + args, **kwargs)
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
    # These directories are created inside the container by `buildvm`:
    ignore = {'target', 'venv'}
    for file_name in listdir(path('.')):
        if file_name in ignore:
            continue
        result[file_name] = file_name
    path_in_docker = lambda p: '/root/%s/%s' % (SETTINGS['app_name'], p)
    return {path(src): path_in_docker(dest) for src, dest in result.items()}

def _get_settings(name):
    return SETTINGS['docker_images'][name]