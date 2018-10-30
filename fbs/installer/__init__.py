from fbs import _defaults, path, LOADED_PROFILES
from fbs.resources import _copy

def _generate_installer_resources():
    for path_fn in _defaults.path, path:
        for profile in LOADED_PROFILES:
            _copy(path_fn, 'src/installer/' + profile, path('target/installer'))