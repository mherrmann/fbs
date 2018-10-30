from fbs import path, SETTINGS, _defaults
from fbs._state import LOADED_PROFILES
from fbs.resources import _copy
from fbs_runtime.platform import is_mac
from os import rename
from os.path import join
from subprocess import run

def run_pyinstaller(extra_args=None, debug=False):
    if extra_args is None:
        extra_args = []
    app_name = SETTINGS['app_name']
    log_level = 'DEBUG' if debug else 'WARN'
    args = [
        'pyinstaller',
        '--name', app_name,
        '--noupx',
        '--log-level', log_level
    ]
    for hidden_import in SETTINGS['hidden_imports']:
        args.extend(['--hidden-import', hidden_import])
    args.extend(extra_args)
    args.extend([
        '--distpath', path('target'),
        '--specpath', path('target/PyInstaller'),
        '--workpath', path('target/PyInstaller'),
        path(SETTINGS['main_module'])
    ])
    if debug:
        args.append('--debug')
    run(args, check=True)
    output_dir = path('target/' + app_name + ('.app' if is_mac() else ''))
    rename(output_dir, path('${freeze_dir}'))

def _generate_resources():
    """
    Copy the data files from src/main/resources to ${freeze_dir}.
    Automatically filters files mentioned in the setting resources_to_filter:
    Placeholders such as ${app_name} are automatically replaced by the
    corresponding setting in files on that list.
    """
    freeze_dir = path('${freeze_dir}')
    if is_mac():
        resources_dest_dir = join(freeze_dir, 'Contents', 'Resources')
    else:
        resources_dest_dir = freeze_dir
    for path_fn in _defaults.path, path:
        for profile in LOADED_PROFILES:
            _copy(path_fn, 'src/main/resources/' + profile, resources_dest_dir)
            _copy(path_fn, 'src/freeze/' + profile, freeze_dir)