from fbs import path
from fbs.builtin_commands import prompt_for_value, require_existing_project
from fbs.builtin_commands._util import extend_json, SECRET_JSON
from fbs.cmdline import command
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import json
import logging

_API_URL = 'https://build-system.fman.io/api'
_LOG = logging.getLogger(__name__)

@command
def register():
    """
    Create an account for uploading your files
    """
    require_existing_project()
    username = prompt_for_value('Username')
    email = prompt_for_value('Real email')
    password = prompt_for_value('Password', password=True)
    status, text = _post_json(_API_URL + '/register', {
        'username': username, 'email': email, 'password': password
    })
    if status == 201:
        if text:
            _LOG.info(text)
        _login(username, password)
    else:
        _LOG.error('Could not register:\n' + text)

@command
def login():
    """
    Save your login credentials to secret.json
    """
    require_existing_project()
    username = prompt_for_value('Username')
    password = prompt_for_value('Password', password=True)
    _login(username, password)

def _login(username, password):
    extend_json(path(SECRET_JSON), {'fbs_user': username, 'fbs_pass': password})
    _LOG.info('Saved your username and password to %s.', SECRET_JSON)

def _post_json(url, data, encoding='utf-8'):
    # We could just use the requests library. But it doesn't pay off to add the
    # whole dependency for just this one function.
    request = Request(url)
    request.add_header('Content-Type', 'application/json; charset=' + encoding)
    data_bytes = json.dumps(data).encode(encoding)
    request.add_header('Content-Length', len(data_bytes))
    try:
        with urlopen(request, data_bytes) as response:
            return response.getcode(), response.read().decode(encoding)
    except HTTPError as e:
        return e.getcode(), e.fp.read().decode(encoding)