from fbs import path
from fbs.installer import _generate_installer_resources
from subprocess import check_call

def create_installer_windows():
    _generate_installer_resources()
    try:
        check_call(['makensis', 'Installer.nsi'], cwd=path('target/installer'))
    except FileNotFoundError:
        raise FileNotFoundError(
            "fbs could not find executable 'makensis'. Please install NSIS and "
            "add its installation directory to your PATH environment variable."
        ) from None