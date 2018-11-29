from fbs import SETTINGS
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
        raise
    lines = output.split('\n')
    for i, line in enumerate(lines):
        if re.match(r'.*\[[^]]*S[^]]*\]$', line):
            for keygrip_line in lines[i + 1:]:
                m = re.match(r' +Keygrip = ([A-Z0-9]{40})', keygrip_line)
                if m:
                    return m.group(1)
    raise RuntimeError('Keygrip not found. Output was:\n' + output)

class GpgDoesNotSupportKeygrip(RuntimeError):
    pass