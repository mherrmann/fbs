from fbs import path, SETTINGS
from fbs_runtime import FbsError
from fbs._state import LOADED_PROFILES
from glob import glob
from os import makedirs
from os.path import dirname, isfile, join, basename, relpath, splitext, exists
from pathlib import Path
from shutil import copy, copymode

import re
import os

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
    Return a list [(size, scale, path)] of available app icons for the current
    platform.
    """
    result = {}
    for profile in LOADED_PROFILES:
        icons_dir = 'src/main/icons/' + profile
        for icon_path in glob(path(icons_dir + '/*.png')):
            name = splitext(basename(icon_path))[0]
            match = re.match('(\d+)(?:@(\d+)x)?', name)
            if not match:
                raise FbsError('Invalid icon name: ' + icon_path)
            size, scale = int(match.group(1)), int(match.group(2) or '1')
            result[(size, scale)] = icon_path
    return [(size, scale, path) for (size, scale), path in result.items()]

def _get_files_to_copy(src_dir_or_file, dest_dir, exclude):
    excludes = _paths(map(path, exclude))
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
        self._paths = []
        # _defaults includes "files_to_filter" - eg. Installer.nsi. If these
        # files don't also exist in the "user's" src/ directory, then
        # Path(p).resolve() raises FileNotFoundError. Handle this:
        for p in paths:
            try:
                self._paths.append(self._resolve_strict(Path(p)))
            except FileNotFoundError:
                pass
    def __contains__(self, item):
        item = Path(item).resolve()
        for p in self._paths:
            if p.samefile(item) or p in item.parents:
                return True
        return False
    def _resolve_strict(self, path_):
        try:
            return path_.resolve(strict=True)
        except TypeError:
            # Python < 3.6:
            return path_.resolve()

def _copy(path_fn, src, dst): # Used by several other internal fbs modules
    src = path_fn(src)
    if exists(src):
        filter_ = [path_fn(f) for f in SETTINGS['files_to_filter']]
        copy_with_filtering(src, dst, files_to_filter=filter_)
        return True
    return False