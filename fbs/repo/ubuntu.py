from fbs import path, _defaults
from fbs._gpg import preset_gpg_passphrase
from fbs.resources import copy_with_filtering
from os import makedirs
from os.path import exists
from shutil import rmtree
from subprocess import check_call, DEVNULL

def create_repo_ubuntu():
    dest_dir = path('target/repo')
    tmp_dir = path('target/repo-tmp')
    if exists(dest_dir):
        rmtree(dest_dir)
    if exists(tmp_dir):
        rmtree(tmp_dir)
    makedirs(tmp_dir)
    distr_file = 'src/repo/ubuntu/distributions'
    distr_path = path(distr_file)
    if not exists(distr_path):
        distr_path = _defaults.path(distr_file)
    copy_with_filtering(distr_path, tmp_dir, files_to_filter=[distr_path])
    preset_gpg_passphrase()
    check_call([
        'reprepro', '-b', dest_dir, '--confdir', tmp_dir,
        'includedeb', 'stable', path('target/${installer}')
    ], stdout=DEVNULL)