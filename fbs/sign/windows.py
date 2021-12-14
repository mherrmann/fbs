from fbs import path, SETTINGS
from fbs_runtime import FbsError
from os import makedirs
from os.path import join, splitext, dirname, basename, exists
from shutil import copy
from subprocess import call, run, DEVNULL

import hashlib
import json
import os

_CERTIFICATE_PATH = 'src/sign/windows/certificate.pfx'
_TO_SIGN = ('.exe', '.cab', '.dll', '.ocx', '.msi', '.xpi')

def sign_windows():
    if not exists(path(_CERTIFICATE_PATH)):
        raise FbsError(
            'Could not find a code signing certificate at:\n    '
            + _CERTIFICATE_PATH
        )
    if 'windows_sign_pass' not in SETTINGS:
        raise FbsError(
            "Please set 'windows_sign_pass' to the password of %s in either "
            "src/build/settings/secret.json, .../windows.json or .../base.json."
            % _CERTIFICATE_PATH
        )
    for subdir, _, files in os.walk(path('${freeze_dir}')):
        for file_ in files:
            extension = splitext(file_)[1]
            if extension in _TO_SIGN:
                sign_file(join(subdir, file_))

def sign_file(file_path, description='', url=''):
    helper = _SignHelper.instance()
    if not helper.is_signed(file_path):
        helper.sign(file_path, description, url)

class _SignHelper:

    _INSTANCE = None

    @classmethod
    def instance(cls):
        if cls._INSTANCE is None:
            cls._INSTANCE = cls(path('cache/signed'))
        return cls._INSTANCE

    def __init__(self, cache_dir):
        self._cache_dir = cache_dir

    def is_signed(self, file_path):
        return not call(
            ['signtool', 'verify', '/pa', file_path], stdout=DEVNULL,
            stderr=DEVNULL
        )

    def sign(self, file_path, description, url):
        json_path = self._get_json_path(file_path)
        try:
            with open(json_path) as f:
                cached = json.load(f)
            is_in_cache = description == cached['description'] and \
                          url == cached['url'] and \
                          self._hash(file_path) == cached['hash']
        except FileNotFoundError:
            is_in_cache = False
        if not is_in_cache:
            self._sign(file_path, description, url)
        copy(self._get_path_in_cache(file_path), file_path)

    def _sign(self, file_path, description, url):
        path_in_cache = self._get_path_in_cache(file_path)
        makedirs(dirname(path_in_cache), exist_ok=True)
        copy(file_path, path_in_cache)
        hash_ = self._hash(path_in_cache)
        self._run_signtool(path_in_cache, 'sha1')
        self._run_signtool(path_in_cache, 'sha256')
        with open(self._get_json_path(file_path), 'w') as f:
            json.dump({
                'description': description,
                'url': url,
                'hash': hash_
            }, f)

    def _get_json_path(self, file_path):
        return self._get_path_in_cache(file_path) + '.json'

    def _get_path_in_cache(self, file_path):
        return join(self._cache_dir, basename(file_path))

    def _run_signtool(self, file_path, digest_alg, description='', url=''):
        password = SETTINGS['windows_sign_pass']
        args = [
            'signtool', 'sign', '/f', path(_CERTIFICATE_PATH), '/p', password
        ]
        if 'windows_sign_server' in SETTINGS:
            args.extend(['/tr', SETTINGS['windows_sign_server']])
        if description:
            args.extend(['/d', description])
        if url:
            args.extend(['/du', url])
        args.extend(['/as', '/fd', digest_alg, '/td', digest_alg])
        args.append(file_path)
        run(args, check=True, stdout=DEVNULL)

    def _hash(self, file_path):
        bufsize = 65536
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            buf = f.read(bufsize)
            while buf:
                hasher.update(buf)
                buf = f.read(bufsize)
        return hasher.hexdigest()