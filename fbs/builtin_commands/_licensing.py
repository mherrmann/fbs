from fbs import path
from fbs.builtin_commands import prompt_for_value, require_existing_project
from fbs.builtin_commands._util import update_json, SECRET_JSON, BASE_JSON
from fbs.cmdline import command

import json
import logging

_LOG = logging.getLogger(__name__)

@command
def init_licensing():
    """
    Generate public/private keys for licensing
    """
    require_existing_project()
    try:
        import rsa
    except ImportError:
        _LOG.error(
            'Please install Python library `rsa`. Eg. via:\n'
            '    pip install rsa'
        )
        return
    nbits = _prompt_for_nbits()
    print('')
    pubkey, privkey = rsa.newkeys(nbits)
    pubkey_args = {'n': pubkey.n, 'e': pubkey.e}
    privkey_args = {
        attr: getattr(privkey, attr) for attr in ('n', 'e', 'd', 'p', 'q')
    }
    update_json(path(SECRET_JSON), {
        'licensing_privkey': privkey_args,
        'licensing_pubkey': pubkey_args
    })
    try:
        with open(path(BASE_JSON)) as f:
            user_base_settings = json.load(f)
    except FileNotFoundError:
        user_base_settings = {}
    public_settings = user_base_settings.get('public_settings', [])
    if 'licensing_pubkey' not in public_settings:
        public_settings.append('licensing_pubkey')
        update_json(path(BASE_JSON), {'public_settings': public_settings})
        updated_base_json = True
    else:
        updated_base_json = False
    message = 'Saved a public/private key pair for licensing to:\n    %s.\n' \
              % SECRET_JSON
    if updated_base_json:
        message += 'Also added "licensing_pubkey" to "public_settings" in' \
                   '\n    %s.\n' \
                   '(This lets your app read the public key when it runs.)\n' \
                   % BASE_JSON
    message += '\nFor details on how to implement licensing for your ' \
               'application, see:\n '\
               '    https://build-system.fman.io/manual#licensing.'
    _LOG.info(message)

def _prompt_for_nbits():
    while True:
        nbits_str = prompt_for_value('Bit size', default='2048')
        try:
            return int(nbits_str)
        except ValueError:
            continue