from fbs_runtime import platform, FbsError
from os.path import join, exists, realpath
from pathlib import PurePath

import errno
import inspect
import os

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

class DevelopmentResourceLocator(ResourceLocator):
    def __init__(self, appctxt_cls):
        project_dir = self._get_project_base_dir(appctxt_cls)
        resources_dir = join(project_dir, 'src', 'main', 'resources')
        resource_dirs = [
            join(resources_dir, platform.name().lower()),
            join(resources_dir, 'base'),
            join(project_dir, 'src', 'main', 'icons')
        ]
        super().__init__(resource_dirs)
    def _get_project_base_dir(self, appctxt_cls):
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