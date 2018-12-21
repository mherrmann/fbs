from fbs import path
from fbs.resources import copy_with_filtering
from fbs_runtime._source import default_path
from os import makedirs, rename
from os.path import exists
from shutil import rmtree, copy
from subprocess import check_call, DEVNULL

def create_repo_fedora():
    if exists(path('target/repo')):
        rmtree(path('target/repo'))
    makedirs(path('target/repo/${version}'))
    copy(path('target/${installer}'), path('target/repo/${version}'))
    check_call(['createrepo_c', '.'], cwd=(path('target/repo')), stdout=DEVNULL)
    repo_file = path('src/repo/fedora/${app_name}.repo')
    use_default = not exists(repo_file)
    if use_default:
        repo_file = default_path('src/repo/fedora/AppName.repo')
    copy_with_filtering(
        repo_file, path('target/repo'), files_to_filter=[repo_file]
    )
    if use_default:
        rename(
            path('target/repo/AppName.repo'),
            path('target/repo/${app_name}.repo')
        )