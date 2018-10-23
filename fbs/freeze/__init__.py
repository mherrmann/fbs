from fbs import path, SETTINGS
from fbs_runtime.platform import is_mac
from os import rename
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