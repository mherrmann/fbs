from fbs import path
from fbs_runtime import FbsError
from getpass import getpass
from os.path import exists
from pathlib import Path

import json
import re

BASE_JSON = 'src/build/settings/base.json'
SECRET_JSON = 'src/build/settings/secret.json'

def prompt_for_value(value, optional=False, default='', password=False):
    message = value
    if default:
        message += ' [%s] ' % default
    message += ': '
    prompt = getpass if password else input
    result = prompt(message).strip()
    if not result and default:
        print(default)
        return default
    if not optional:
        while not result:
            result = prompt(message).strip()
    return result

def require_existing_project():
    if not exists(path('src')):
        raise FbsError(
            "Could not find the src/ directory. Are you in the right folder?\n"
            "If yes, did you already run\n"
            "    fbs startproject ?"
        )

def extend_json(f_path, dict_):
    f = Path(f_path)
    try:
        contents = f.read_text()
    except FileNotFoundError:
        indent = _get_indent(_split_json(Path(path(BASE_JSON)).read_text())[1])
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