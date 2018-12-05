from fbs import path, SETTINGS
from fbs.builtin_commands._docker import _run_docker
from fbs.builtin_commands._util import prompt_for_value, \
    require_existing_project
from fbs.cmdline import command
from fbs_runtime import FbsError
from os import makedirs
from os.path import dirname, exists
from pathlib import Path
from subprocess import DEVNULL, PIPE

import json
import logging
import re

_LOG = logging.getLogger(__name__)
_DOCKER_IMAGE = 'fbs:gpg_generator'
_DEST_DIR = 'src/sign/linux'
_PUBKEY_NAME = 'public-key.gpg'
_PRIVKEY_NAME = 'private-key.gpg'
_BASE_JSON = 'src/build/settings/base.json'
_SECRET_JSON = 'src/build/settings/secret.json'

@command
def gengpgkey():
    """
    Generate a GPG key for code signing on Linux
    """
    require_existing_project()
    if exists(_DEST_DIR):
        raise FbsError('The %s folder already exists. Aborting.' % _DEST_DIR)
    try:
        email = prompt_for_value('Email address')
        name = prompt_for_value('Real name', default=SETTINGS['author'])
        passphrase = prompt_for_value('Key password', password=True)
    except KeyboardInterrupt:
        print('')
        return
    _LOG.info('Generating the GPG key. This can take a little...')
    _init_docker()
    args = ['run', '-t']
    if exists('/dev/urandom'):
        # Give the key generator more entropy on Posix:
        args.extend(['-v', '/dev/urandom:/dev/random'])
    args.extend([_DOCKER_IMAGE, '/root/genkey.sh', name, email, passphrase])
    result = _run_docker(args, check=True, stdout=PIPE, universal_newlines=True)
    key = _snip(
        result.stdout,
        "revocation certificate stored as '/root/.gnupg/openpgp-revocs.d/",
        ".rev'",
        include_bounds=False
    )
    pubkey = _snip(result.stdout,
                   '-----BEGIN PGP PUBLIC KEY BLOCK-----\n',
                   '-----END PGP PUBLIC KEY BLOCK-----\n')
    privkey = _snip(result.stdout,
                    '-----BEGIN PGP PRIVATE KEY BLOCK-----\n',
                    '-----END PGP PRIVATE KEY BLOCK-----\n')
    makedirs(path(_DEST_DIR), exist_ok=True)
    pubkey_dest = _DEST_DIR + '/' + _PUBKEY_NAME
    Path(path(pubkey_dest)).write_text(pubkey)
    Path(path(_DEST_DIR + '/' + _PRIVKEY_NAME)).write_text(privkey)
    _extend_json(path(_BASE_JSON), { 'gpg_key': key, 'gpg_name': name })
    _extend_json(path(_SECRET_JSON), { 'gpg_pass': passphrase })
    _LOG.info(
        'Done. Created %s and ...%s. Also updated %s and ...secret.json with '
        'the values you provided.', pubkey_dest, _PRIVKEY_NAME, _BASE_JSON
    )

def _init_docker():
    _run_docker(
        ['build', '-t', _DOCKER_IMAGE, dirname(__file__)], stdout=DEVNULL
    )

def _snip(str_, preamble, postamble, include_bounds=True):
    start = str_.index(preamble)
    end = str_.index(postamble, start + len(preamble))
    if not include_bounds:
        start += len(preamble)
    if include_bounds:
        end += len(postamble)
    return str_[start:end]

def _extend_json(f_path, dict_):
    f = Path(f_path)
    try:
        contents = f.read_text()
    except FileNotFoundError:
        indent = _get_indent(_split_json(Path(path(_BASE_JSON)).read_text())[1])
        new_contents = json.dumps(dict_, indent=indent)
    else:
        new_contents = _extend_json_str(contents, dict_)
    f.write_text(new_contents)

def _extend_json_str(json_str, dict_):
    if not dict_:
        return json_str
    start, body, end = _split_json(json_str)
    indent = _get_indent(body)
    append = json.dumps(dict_, indent=indent)[1:-1]
    new_body = body.rstrip() + ',' + append
    return start + new_body + end

def _split_json(f_contents):
    start = f_contents.index('{')
    end = f_contents.rindex('}', start + 1)
    return f_contents[:start], f_contents[start:end], f_contents[end:]

def _get_indent(json_body):
    match = re.search('\n(\\s+)', json_body)
    return match.group(1) if match else ''