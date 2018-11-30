from fbs import path
from fbs._gpg import preset_gpg_passphrase
from subprocess import check_call, DEVNULL

def sign_installer_fedora():
    # Prevent GPG from prompting us for the passphrase when signing:
    preset_gpg_passphrase()
    check_call(
        ['rpm', '--addsign', path('target/${installer}')], stdout=DEVNULL
    )