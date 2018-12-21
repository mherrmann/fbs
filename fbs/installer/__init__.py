from fbs import path, LOADED_PROFILES
from fbs.resources import _copy
from fbs_runtime._source import default_path

def _generate_installer_resources():
    for path_fn in default_path, path:
        for profile in LOADED_PROFILES:
            _copy(path_fn, 'src/installer/' + profile, path('target/installer'))