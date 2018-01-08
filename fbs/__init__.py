from fbs import platform
from os.path import normpath, join, isabs, dirname, exists, abspath

import json

SETTINGS = {}

def init(project_dir):
    """
    Only call this if you are not running `python -m fbs` or fbs.cmdline.main().
    """
    SETTINGS['project_dir'] = abspath(project_dir)
    activate_profile('base')
    activate_profile(platform.name().lower())

def activate_profile(profile_name):
    _LOADED_PROFILES.append(profile_name)
    default_settings = join(dirname(__file__), 'default_settings')
    project_settings = path('src/build/settings')
    json_paths = [
        join(dir_path, profile + '.json')
        for dir_path in (default_settings, project_settings)
        for profile in _LOADED_PROFILES
    ]
    SETTINGS.update(_load_settings(p for p in json_paths if exists(p)))

_LOADED_PROFILES = []

def path(path_str):
    path_str = _expand_placeholders(path_str)
    if isabs(path_str):
        return path_str
    try:
        project_dir = SETTINGS['project_dir']
    except KeyError:
        error_message = "Cannot call path(...) until fbs.init(...) has been " \
                        "called."
        raise RuntimeError(error_message) from None
    return normpath(join(project_dir, *path_str.split('/')))

def _load_settings(json_paths):
    result = {}
    for json_path in json_paths:
        with open(json_path, 'r') as f:
            result.update(json.load(f))
    while True:
        for key, value in result.items():
            if isinstance(value, str):
                new_value = _expand_placeholders(value, result)
                if new_value != value:
                    result[key] = new_value
                    break
        else:
            break
    return result

def _expand_placeholders(str_, settings=None):
    if settings is None:
        settings = SETTINGS
    for key, value in settings.items():
        str_ = str_.replace('${%s}' % key, str(value))
    return str_