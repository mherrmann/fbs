from fbs import path, SETTINGS
from fbs._state import LOADED_PROFILES
from fbs_runtime.platform import is_mac
from glob import glob
from os import makedirs
from os.path import exists, dirname, isfile, join, basename, relpath, splitext
from pathlib import Path
from shutil import copy, copymode

import os

def generate_resources():
    """
    Copy the data files from src/main/resources to the target/ directory.
    Automatically filters files mentioned in the setting resources_to_filter:
    Placeholders such as ${app_name} are automatically replaced by the
    corresponding setting in files on that list.
    """
    freeze_dir = path('${freeze_dir}')
    if is_mac():
        resources_dest_dir = join(freeze_dir, 'Contents', 'Resources')
    else:
        resources_dest_dir = freeze_dir
    kwargs = {'files_to_filter': SETTINGS['resources_to_filter']}
    resource_dirs = [
        path('src/main/resources/' + profile) for profile in LOADED_PROFILES
    ]
    for dir_ in resource_dirs:
        if exists(dir_):
            copy_with_filtering(dir_, resources_dest_dir, **kwargs)
        frozen_resources_dir = dir_ + '-frozen'
        if exists(frozen_resources_dir):
            copy_with_filtering(frozen_resources_dir, freeze_dir, **kwargs)

def copy_with_filtering(
    src_dir_or_file, dest_dir, replacements=None, files_to_filter=None,
    exclude=None, placeholder='${%s}'
):
    """
    Copy the given file or directory to the given destination, optionally
    applying filtering.
    """
    if replacements is None:
        replacements = SETTINGS
    if files_to_filter is None:
        files_to_filter = []
    if exclude is None:
        exclude = []
    to_copy = _get_files_to_copy(src_dir_or_file, dest_dir, exclude)
    to_filter = _paths(files_to_filter)
    for src, dest in to_copy:
        makedirs(dirname(dest), exist_ok=True)
        if files_to_filter is None or src in to_filter:
            _copy_with_filtering(src, dest, replacements, placeholder)
        else:
            copy(src, dest)

def get_icons():
    """
    Return a list [(size_in_pixels, path)] of available app icons for the
    current platform.
    """
    result = {}
    for profile in LOADED_PROFILES:
        icons_dir = 'src/main/icons/' + profile
        for icon_path in glob(path(icons_dir + '/*.png')):
            size = int(splitext(basename(icon_path))[0])
            result[size] = icon_path
    return list(result.items())

def _get_files_to_copy(src_dir_or_file, dest_dir, exclude):
    excludes = _paths(exclude)
    if isfile(src_dir_or_file) and src_dir_or_file not in excludes:
        yield src_dir_or_file, join(dest_dir, basename(src_dir_or_file))
    else:
        for (subdir, _, files) in os.walk(src_dir_or_file):
            dest_subdir = join(dest_dir, relpath(subdir, src_dir_or_file))
            for file_ in files:
                file_path = join(subdir, file_)
                dest_path = join(dest_subdir, file_)
                if file_path not in excludes:
                    yield file_path, dest_path

def _copy_with_filtering(
    src_file, dest_file, dict_, placeholder='${%s}', encoding='utf-8'
):
    replacements = []
    for key, value in dict_.items():
        old = (placeholder % key).encode(encoding)
        new = str(value).encode(encoding)
        replacements.append((old, new))
    with open(src_file, 'rb') as open_src_file:
        with open(dest_file, 'wb') as open_dest_file:
            for line in open_src_file:
                new_line = line
                for old, new in replacements:
                    new_line = new_line.replace(old, new)
                open_dest_file.write(new_line)
        copymode(src_file, dest_file)

class _paths:
    def __init__(self, paths):
        self._paths = [Path(path(p)).resolve() for p in paths]
    def __contains__(self, item):
        item = Path(item).resolve()
        for p in self._paths:
            if p.samefile(item) or p in item.parents:
                return True
        return False