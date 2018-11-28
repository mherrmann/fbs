from fbs import path
from fbs_runtime import FbsError
from getpass import getpass
from os.path import exists

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