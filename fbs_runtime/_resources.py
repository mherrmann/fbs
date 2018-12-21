from os.path import join, exists, realpath

import errno
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