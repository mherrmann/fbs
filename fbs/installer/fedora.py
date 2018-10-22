from fbs.installer.linux import generate_installer_files, run_fpm

def create_installer_fedora():
    generate_installer_files()
    run_fpm('rpm')