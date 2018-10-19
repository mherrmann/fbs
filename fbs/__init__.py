from fbs import _state
from fbs._state import LOADED_PROFILES
from fbs_runtime import platform
from fbs_runtime.platform import is_ubuntu
from os.path import normpath, join, isabs, dirname, exists, abspath

import json

"""
fbs populates SETTINGS with the current build settings. A typical example is
SETTINGS['app_name'], which you define in src/build/settings/base.json.
"""
SETTINGS = _state.SETTINGS

def init(project_dir):
    """
    Call this if you are not invoking `python -m fbs` or fbs.cmdline.main().
    """
    SETTINGS['project_dir'] = abspath(project_dir)
    activate_profile('base')
    activate_profile(platform.name().lower())
    if is_ubuntu():
        activate_profile('ubuntu')

def activate_profile(profile_name):
    """
    By default, fbs only loads src/build/settings/base.json and .../os.json
    where `os` is one of "mac", "linux" and "windows". This function lets you
    load other settings on the fly. A common example would be distinguishing
    between different Linux distributions (eg. ubuntu.json / arch.json).
    Or in custom build scripts during a release, where release.json contains the
    production server URL instead of a staging server.
    """
    LOADED_PROFILES.append(profile_name)
    default_settings = join(dirname(__file__), 'default_settings')
    project_settings = path('src/build/settings')
    json_paths = [
        join(dir_path, profile + '.json')
        for dir_path in (default_settings, project_settings)
        for profile in LOADED_PROFILES
    ]
    SETTINGS.update(_load_settings(p for p in json_paths if exists(p)))

def path(path_str):
    """
    Return the absolute path of the given file in the project directory. For
    instance: path('src/main/python'). The `path_str` argument should always use
    forward slashes `/`, even on Windows. You can use placeholders to refer to
    settings. For example: path('${freeze_dir}/foo').
    """
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
    """
    Return settings from the given JSON files as a dictionary. This function
    expands placeholders: That is, if a settings file contains
        {
            "app_name": "MyApp",
            "freeze_dir": "target/${app_name}"
        }
    then "freeze_dir" in the result of this function is "target/MyApp".
    """
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