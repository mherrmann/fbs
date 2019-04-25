"""
This module contains functions that should only be called by module `fbs`, or
when running from source.
"""

from fbs_runtime import FbsError
from fbs_runtime._fbs import get_default_profiles, get_core_settings, \
    filter_public_settings
from fbs_runtime._settings import load_settings
from os.path import join, normpath, dirname, pardir, exists
from pathlib import Path

import os

def get_project_dir():
    result = Path(os.getcwd())
    while result != result.parent:
        if (result / 'src' / 'main' / 'python').is_dir():
            return str(result)
        result = result.parent
    raise FbsError(
        'Could not determine the project base directory. '
        'Was expecting src/main/python.'
    )

def get_resource_dirs(project_dir):
    resources = path(project_dir, 'src/main/resources')
    result = [join(resources, profile) for profile in get_default_profiles()]
    result.append(path(project_dir, 'src/main/icons'))
    return result

def load_build_settings(project_dir):
    core_settings = get_core_settings(project_dir)
    profiles = get_default_profiles()
    json_paths = get_settings_paths(project_dir, profiles)
    all_settings = load_settings(json_paths, core_settings)
    return filter_public_settings(all_settings)

def get_settings_paths(project_dir, profiles):
    return list(filter(exists, (
        path_fn('src/build/settings/%s.json' % profile)
        for path_fn in (default_path, lambda p: path(project_dir, p))
        for profile in profiles
    )))

def default_path(path_str):
    defaults_dir = join(dirname(__file__), pardir, 'fbs', '_defaults')
    return path(defaults_dir, path_str)

def path(base_dir, path_str):
    return normpath(join(base_dir, *path_str.split('/')))