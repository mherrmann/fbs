from fbs import _state, _defaults
from fbs._settings import load_settings, expand_placeholders
from fbs._state import LOADED_PROFILES
from fbs_runtime import platform
from fbs_runtime.platform import is_ubuntu, is_linux, is_arch_linux, is_fedora
from os.path import normpath, join, exists, abspath

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
    if is_linux():
        if is_ubuntu():
            activate_profile('ubuntu')
        elif is_arch_linux():
            activate_profile('arch')
        elif is_fedora():
            activate_profile('fedora')

def activate_profile(profile_name):
    """
    By default, fbs only loads src/build/settings/base.json and .../`os`.json
    where `os` is one of "mac", "linux" and "windows". This function lets you
    load other settings on the fly. A common example would be distinguishing
    between different Linux distributions (eg. ubuntu.json / arch.json).
    Or in custom build scripts during a release, where release.json contains the
    production server URL instead of a staging server.
    """
    LOADED_PROFILES.append(profile_name)
    json_paths = [
        path_fn('src/build/settings/%s.json' % profile)
        for path_fn in (_defaults.path, path)
        for profile in LOADED_PROFILES
    ]
    SETTINGS.update(load_settings(p for p in json_paths if exists(p)))

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
        raise RuntimeError(error_message) from None
    return normpath(join(project_dir, *path_str.split('/')))