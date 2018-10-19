from fbs.cmdline import command
from fbs.installer.linux import generate_installer_files, run_fpm

@command
def create_installer_ubuntu():
    generate_installer_files()
    run_fpm('deb')