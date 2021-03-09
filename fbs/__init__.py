from fbs import _state
from fbs._state import LOADED_PROFILES
from fbs_runtime import FbsError, _source
from fbs_runtime._fbs import get_core_settings, get_default_profiles
from fbs_runtime._settings import load_settings, expand_placeholders
from fbs_runtime._source import get_settings_paths
from os.path import abspath

import sys

"""
fbs populates SETTINGS with the current build settings. A typical example is
SETTINGS['app_name'], which you define in src/build/settings/base.json.
"""
SETTINGS = _state.SETTINGS

def init(project_dir):
    """
    Call this if you are invoking neither `fbs` on the command line nor
    fbs.cmdline.main() from Python.
    """
    if sys.version_info[0] != 3 or sys.version_info[1] not in (5, 6):
        raise FbsError(
            'The free version of fbs only supports Python 3.5 and 3.6.\n'
            'Please obtain fbs Pro from https://build-system.fman.io/pro.'
        )
    SETTINGS.update(get_core_settings(abspath(project_dir)))
    for profile in get_default_profiles():
        activate_profile(profile)

def activate_profile(profile_name):
    """
    By default, fbs only loads some settings. For instance,
    src/build/settings/base.json and .../`os`.json where `os` is one of "mac",
    "linux" or "windows". This function lets you load other settings on the fly.
    A common example would be during a release, where release.json contains the
    production server URL instead of a staging server.
    """
    LOADED_PROFILES.append(profile_name)
    project_dir = SETTINGS['project_dir']
    json_paths = get_settings_paths(project_dir, LOADED_PROFILES)
    core_settings = get_core_settings(project_dir)
    SETTINGS.update(load_settings(json_paths, core_settings))

def path(path_str):
    """
    Return the absolute path of the given file in the project directory. For
    instance: path('src/main/python'). The `path_str` argument should always use
    forward slashes `/`, even on Windows. You can use placeholders to refer to
    settings. For example: path('${freeze_dir}/foo').
    """
    path_str = expand_placeholders(path_str, SETTINGS)
    try:
        project_dir = SETTINGS['project_dir']
    except KeyError:
        error_message = "Cannot call path(...) until fbs.init(...) has been " \
                        "called."
        raise FbsError(error_message) from None
    return _source.path(project_dir, path_str)