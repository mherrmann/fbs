from fbs_runtime import platform, FbsError
from fbs_runtime.platform import is_mac
from os.path import join, exists, realpath, dirname, pardir
from pathlib import PurePath

import errno
import inspect
import os
import sys

class ResourceLocator:
    def __init__(self, resource_dirs):
        self._dirs = resource_dirs
    def locate(self, *rel_path):
        for resource_dir in self._dirs:
            resource_path = join(resource_dir, *rel_path)
            if exists(resource_path):
                return realpath(resource_path)
        raise FileNotFoundError(
            errno.ENOENT, 'Could not locate resource', os.sep.join(rel_path)
        )

def get_resource_dirs_frozen():
    app_dir = dirname(sys.executable)
    return [join(app_dir, pardir, 'Resources') if is_mac() else app_dir]

def get_resource_dirs_source(appctxt_cls):
    project_dir = _get_project_base_dir(appctxt_cls)
    resources_dir = join(project_dir, 'src', 'main', 'resources')
    return [
        join(resources_dir, platform.name().lower()),
        join(resources_dir, 'base'),
        join(project_dir, 'src', 'main', 'icons')
    ]

def _get_project_base_dir(appctxt_cls):
    class_file = inspect.getfile(appctxt_cls)
    p = PurePath(class_file)
    while p != p.parent:
        parent_names = [p.parents[2].name, p.parents[1].name, p.parent.name]
        if parent_names == ['src', 'main', 'python']:
            return str(p.parents[3])
        p = p.parent
    raise FbsError(
        'Could not determine project base directory for %s. Is it in '
        'src/main/python?' % appctxt_cls
    )