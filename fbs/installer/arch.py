from fbs import path
from fbs.installer.linux import generate_installer_files, run_fpm
from subprocess import run

def create_installer_arch():
    generate_installer_files()
    # Avoid pacman warning "directory permissions differ" when installing:
    run(['chmod', 'g-w', '-R', path('target/installer')], check=True)
    run_fpm('pacman')