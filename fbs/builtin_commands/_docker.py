from fbs import path, SETTINGS, _defaults
from fbs.builtin_commands import require_existing_project
from fbs.cmdline import command
from fbs.resources import _copy
from fbs_runtime import FbsError
from gitignore_parser import parse_gitignore
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
    Build a virtual machine. Eg.: buildvm ubuntu
    """
    require_existing_project()
    build_dir = path('target/%s-docker-image' % name)
    if exists(build_dir):
        rmtree(build_dir)
    src_root = 'src/build/docker'
    available_vms = set(listdir(_defaults.path(src_root)))
    if exists(path(src_root)):
        available_vms.update(listdir(path(src_root)))
    if name not in available_vms:
        raise FbsError(
            'Could not find %s. Available VMs are:%s' %
            (name, ''.join(['\n * ' + vm for vm in available_vms]))
        )
    src_dir = src_root + '/' + name
    for path_fn in _defaults.path, path:
        _copy(path_fn, src_dir, build_dir)
    settings = SETTINGS['docker_images'].get(name, {})
    for path_fn in _defaults.path, path:
        for p in settings.get('build_files', []):
            _copy(path_fn, p, build_dir)
    args = ['build', '--pull', '-t', _get_docker_id(name), build_dir]
    for arg, value in settings.get('build_args', {}).items():
        args.extend(['--build-arg', '%s=%s' % (arg, value)])
    try:
        _run_docker(args, check=True, stdout=PIPE, universal_newlines=True)
    except CalledProcessError as e:
        raise FbsError(e.stdout)
    _LOG.info('Done. You can now execute:\n    fbs runvm ' + name)

@command
def runvm(name):
    """
    Run a virtual machine. Eg.: runvm ubuntu
    """
    args = ['run', '-it']
    for item in _get_docker_mounts(name).items():
        args.extend(['-v', '%s:%s' % item])
    args.append(_get_docker_id(name))
    _LOG.info(
        "You are now in a Docker container running %s. To build your app for "
        "this platform, use the normal commands `fbs freeze` etc.\n\n"
        "Note that you can't launch GUIs here. So eg. `fbs run` won't work.\n\n"
        "Another caveat is that target/ here is special: It symlinks to your "
        "usual target/%s/. So when you are done and type `exit` to leave this "
        "container, you can find the produced binaries there.",
        name.title(), name
    )
    _run_docker(args)

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
    gitignore = path('.gitignore')
    if not exists(gitignore):
        gitignore = _defaults.path('.gitignore')
    is_in_gitignore = parse_gitignore(gitignore, base_dir=path('.'))
    for file_name in listdir(path('.')):
        if is_in_gitignore(path(file_name)):
            continue
        result[file_name] = file_name
    path_in_docker = lambda p: '/root/%s/%s' % (SETTINGS['app_name'], p)
    return {path(src): path_in_docker(dest) for src, dest in result.items()}

def _get_settings(name):
    return SETTINGS['docker_images'][name]