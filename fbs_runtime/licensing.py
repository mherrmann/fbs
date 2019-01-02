from base64 import b64encode, b64decode
from rsa import PrivateKey, PublicKey, VerificationError

import json
import rsa

def pack_license_key(data, privkey_args):
    """
    Pack a dictionary of license key data to a string. You typically call this
    function on a server, when a user purchases a license. Eg.:

        lk_contents = pack_license_key({'email': 'some@user.com'}, ...)

    The parameter `privkey_args` is a dictionary containing values for the RSA
    fields "n", "e", "d", "p" and "q". You can generate it with fbs's command
    `init_licensing`.

    The resulting string is signed to prevent the end user from changing it.
    Use the function `unpack_license_key` below to reconstruct `data` from it.
    This also verifies that the string was not tampered with.

    This function has two non-obvious caveats:

    1) It does not obfuscate the data. If `data` contains "key": "value", then
       "key": "value" is also visible in the resulting string.

    2) Calling this function twice with the same arguments will result in the
    same string. This may be undesirable when you generate multiple license keys
    for the same user. A simple workaround for this is to add a unique parameter
    to `data`, such as the current timestamp.
    """
    data_bytes = _dumpb(data)
    signature = rsa.sign(data_bytes, PrivateKey(**privkey_args), 'SHA-1')
    result = dict(data)
    if 'key' in data:
        raise ValueError('Data must not contain an element called "key"')
    result['key'] = b64encode(signature).decode('ascii')
    return json.dumps(result)

class _Licensing:
    """
    This internal class lets us inject the licensing functionality into the
    application context, in such a way that the fbs user does not have to worry
    about where the public key is stored.
    """
    def __init__(self, pubkey_args):
        self._pubkey = pubkey_args
    def unpack_license_key(self, key_str):
        return unpack_license_key(key_str, self._pubkey)

class InvalidKey(Exception):
    pass

def unpack_license_key(key_str, pubkey_args):
    """
    Decode a string of license key data produced by `pack_license_key`. In other
    words, this function is the inverse of `pack_...` above:

        data == unpack_license_key(pack_license_key(data, ...), ...)

    If the given string is not a valid key, `InvalidKey` is raised.

    The parameter `pubkey_args` is a dictionary containing values for the RSA
    fields "n" and "e". It can be generated with fbs's command `init_licensing`.
    """
    try:
        result = json.loads(key_str)
    except ValueError:
        raise InvalidKey() from None
    try:
        signature = result.pop('key')
    except KeyError:
        raise InvalidKey() from None
    try:
        signature_bytes = b64decode(signature.encode('ascii'))
    except ValueError:
        raise InvalidKey() from None
    try:
        rsa.verify(_dumpb(result), signature_bytes, PublicKey(**pubkey_args))
    except VerificationError:
        raise InvalidKey() from None
    return result

def _dumpb(dict_):
    return json.dumps(dict_, sort_keys=True).encode('utf-8')