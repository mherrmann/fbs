from collections import OrderedDict
from fbs import path
from fbs_runtime import FbsError
from getpass import getpass
from os.path import exists
from pathlib import Path

import json
import re

BASE_JSON = 'src/build/settings/base.json'
SECRET_JSON = 'src/build/settings/secret.json'

def prompt_for_value(
    value, optional=False, default='', password=False, choices=()
):
    message = value
    if choices:
        choices_dict = \
            OrderedDict((str(i + 1), c) for (i, c) in enumerate(choices))
        message += ': '
        message += ' or '.join('%s) %s' % tpl for tpl in choices_dict.items())
    if default:
        message += ' [%s] ' % \
                   (choices.index(default) + 1 if choices else default)
    message += ': '
    prompt = getpass if password else input
    result = prompt(message).strip()
    if not result and default:
        print(default)
        return default
    if not optional:
        while not result or (choices and result not in choices_dict):
            result = prompt(message).strip()
    return choices_dict[result] if choices else result

def require_existing_project():
    if not exists(path('src')):
        raise FbsError(
            "Could not find the src/ directory. Are you in the right folder?\n"
            "If yes, did you already run\n"
            "    fbs startproject ?"
        )

def update_json(f_path, dict_):
    f = Path(f_path)
    try:
        contents = f.read_text()
    except FileNotFoundError:
        indent = _infer_indent(Path(path(BASE_JSON)).read_text())
        new_contents = json.dumps(dict_, indent=indent)
    else:
        new_contents = _update_json_str(contents, dict_)
    f.write_text(new_contents)

def _update_json_str(json_str, dict_):
    if not dict_:
        return json_str
    data = json.loads(json_str, object_pairs_hook=OrderedDict)
    data.update(dict_)
    indent = _infer_indent(json_str)
    return json.dumps(data, indent=indent)

def _infer_indent(json_str):
    start = json_str.find('{')
    if start == -1:
        return None
    match = re.search('\n(\\s+)', json_str[start:])
    return match.group(1) if match else None