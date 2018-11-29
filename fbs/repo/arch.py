from fbs import path, SETTINGS
from fbs_runtime import FbsError
from os import makedirs
from os.path import exists, join
from shutil import rmtree, copy
from subprocess import check_call, DEVNULL

def create_repo_arch():
    if not exists(path('target/${installer}.sig')):
        raise FbsError(
            'Installer does not exist or is not signed. Maybe you need to '
            'run:\n'
            '    fbs signinst'
        )
    dest_dir = path('target/repo')
    if exists(dest_dir):
        rmtree(dest_dir)
    makedirs(dest_dir)
    app_name = SETTINGS['app_name']
    pkg_file = path('target/${installer}')
    pkg_file_versioned = '%s-%s.pkg.tar.xz' % (app_name, SETTINGS['version'])
    copy(pkg_file, join(dest_dir, pkg_file_versioned))
    copy(pkg_file + '.sig', join(dest_dir, pkg_file_versioned + '.sig'))
    check_call(
        ['repo-add', '%s.db.tar.gz' % app_name, pkg_file_versioned],
        cwd=dest_dir, stdout=DEVNULL
    )
    # Ensure the permissions are correct if uploading to a server:
    check_call(['chmod', 'g-w', '-R', dest_dir])