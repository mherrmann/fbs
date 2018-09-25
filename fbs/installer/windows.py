from fbs import path, SETTINGS
from fbs.resources import copy_with_filtering
from os.path import join
from subprocess import run

def create_installer_windows():
    nsis_dir = path('src/main/NSIS')
    copy_with_filtering(
        nsis_dir,
        path('target/NSIS'),
        replacements={
            'app_name': SETTINGS['app_name'],
            'author': SETTINGS['author']
        },
        files_to_filter=[join(nsis_dir, 'Installer.nsi')],
        placeholder='%%{%s}'
    )
    try:
        run(['makensis', 'Installer.nsi'], cwd=path('target/NSIS'), check=True)
    except FileNotFoundError:
        raise FileNotFoundError(
            "fbs could not find executable 'makensis'. Please install NSIS and "
            "add its installation directory to your PATH environment variable."
        ) from None