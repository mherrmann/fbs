"""
This module contains functions that should only be called by module `fbs`, or
when running from source.
"""

from fbs_runtime import FbsError
from fbs_runtime._fbs import get_default_profiles, get_core_settings, \
    filter_public_settings
from fbs_runtime._settings import load_settings, merge_settings
from os.path import join, normpath, dirname, pardir, exists
from pathlib import Path

import os

def get_project_dir():
    result = Path(os.getcwd())
    while result != result.parent:
        if (result / 'src' / 'build' / 'settings').is_dir() or Path('fbs_directories.json').is_file():
            return str(result)
        result = result.parent
    raise FbsError(
        'Could not determine the project base directory. '
        'Was expecting src/build/settings or fbs_directories.json.'
    )

def get_resource_dirs(project_dir, settings):
    result = [path(project_dir, settings['icons_dir'])]
    resources = path(project_dir, settings['resources_dir'])
    result.extend(
        join(resources, profile)
        # Resource dirs are listed most-specific first whereas profiles are
        # listed most-specific last. We therefore need to reverse the order:
        for profile in reversed(get_default_profiles())
    )
    return result

def load_build_settings(project_dir):
    core_settings = get_core_settings(project_dir)
    profiles = get_default_profiles()

    all_settings = load_settings_from_paths(project_dir, profiles, core_settings)

    return filter_public_settings(all_settings)

def load_settings_from_paths(project_dir, profiles, core_settings):
    initial_settings_paths = get_settings_paths(lambda p: default_path("src/build/settings/%s" % p), profiles)

    path_settings_file = path(project_dir, "fbs_directories.json")
    if exists(path_settings_file):
        initial_settings_paths.append(path_settings_file)

    initial_settings = load_settings(initial_settings_paths, core_settings)

    # extract project settings paths
    user_settings_dirs = get_settings_paths(
        lambda p: path(project_dir, "%s/%s" % (initial_settings['settings_dir'], p)), profiles)

    user_settings = load_settings(user_settings_dirs)

    return merge_settings(initial_settings, user_settings)

def get_settings_paths(path_fn, profiles):
    build_settings_paths = list(filter(exists, (
        path_fn('%s.json' % profile)
        for profile in profiles
    )))

    return build_settings_paths

def default_path(path_str):
    defaults_dir = join(dirname(__file__), pardir, 'fbs', '_defaults')
    return path(defaults_dir, path_str)

def path(base_dir, path_str):
    return normpath(join(base_dir, *path_str.split('/')))