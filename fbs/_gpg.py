from fbs import SETTINGS
from fbs_runtime import FbsError
from subprocess import run, DEVNULL, check_call, check_output, PIPE, \
    CalledProcessError

import re

def preset_gpg_passphrase():
    # Ensure gpg-agent is running:
    run(
        ['gpg-agent', '--daemon', '--use-standard-socket', '-q'],
        stdout=DEVNULL, stderr=DEVNULL
    )
    gpg_key = SETTINGS['gpg_key']
    try:
        keygrip = _get_keygrip(gpg_key)
    except GpgDoesNotSupportKeygrip:
        # Old GPG versions don't support keygrips; They use the fingerprint
        # instead:
        keygrip = gpg_key
    check_call([
        SETTINGS['gpg_preset_passphrase'], '--preset', '--passphrase',
        SETTINGS['gpg_pass'], keygrip
    ], stdout=DEVNULL)

def _get_keygrip(pubkey_id):
    try:
        output = check_output(
            ['gpg2', '--with-keygrip', '-K', pubkey_id],
            universal_newlines=True, stderr=PIPE
        )
    except CalledProcessError as e:
        if 'invalid option "--with-keygrip"' in e.stderr:
            raise GpgDoesNotSupportKeygrip() from None
        elif 'No secret key' in e.stderr:
            raise FbsError(
                "GPG could not read your key for code signing. Perhaps you "
                "don't want\nto run this command here, but after:\n"
                "    fbs runvm {ubuntu|fedora|arch}"
            )
        raise
    pure_signing_subkey = _find_keygrip(output, 'S')
    if pure_signing_subkey:
        return pure_signing_subkey
    any_signing_key = _find_keygrip(output, '[^]]*S[^]]*')
    if any_signing_key:
        return any_signing_key
    raise RuntimeError('Keygrip not found. Output was:\n' + output)

def _find_keygrip(gpg2_output, type_re):
    lines = gpg2_output.split('\n')
    for i, line in enumerate(lines):
        if re.match(r'.*\[%s\]$' % type_re, line):
            for keygrip_line in lines[i + 1:]:
                m = re.match(r' +Keygrip = ([A-Z0-9]{40})', keygrip_line)
                if m:
                    return m.group(1)

class GpgDoesNotSupportKeygrip(RuntimeError):
    pass