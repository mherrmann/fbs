from fbs import path, SETTINGS
from fbs._gpg import preset_gpg_passphrase
from subprocess import check_call, DEVNULL

def sign_installer_arch():
    installer = path('target/${installer}')
    # Prevent GPG from prompting us for the passphrase when signing:
    preset_gpg_passphrase()
    check_call(
        ['gpg', '--batch', '--yes', '-u', SETTINGS['gpg_key'],
        '--output', installer + '.sig', '--detach-sig', installer],
        stdout=DEVNULL
    )