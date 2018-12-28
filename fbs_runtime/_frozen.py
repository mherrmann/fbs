"""
This module contains functions that should only be called when running the
frozen form of the app.
"""

from os.path import dirname, join, pardir
from fbs_runtime.platform import is_mac

import sys

# The contents of this dictionary are injected via a PyInstaller runtime hook.
# See: `fbs.freeze._PyInstallerRuntimehook`.
BUILD_SETTINGS = {}

def get_resource_dirs():
    app_dir = dirname(sys.executable)
    return [join(app_dir, pardir, 'Resources') if is_mac() else app_dir]

def load_build_settings():
    return BUILD_SETTINGS