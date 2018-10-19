from fbs import path, SETTINGS
from fbs_runtime.platform import is_mac
from os import rename
from subprocess import run

def run_pyinstaller(extra_args=None, debug=False):
    if extra_args is None:
        extra_args = []
    app_name = SETTINGS['app_name']
    log_level = 'DEBUG' if debug else 'WARN'
    cmdline = [
        'pyinstaller',
        '--name', app_name,
        '--noupx',
        '--log-level', log_level
    ] + extra_args + [
        '--distpath', path('target'),
        '--specpath', path('target/PyInstaller'),
        '--workpath', path('target/PyInstaller'),
        path(SETTINGS['main_module'])
    ]
    if debug:
        cmdline.append('--debug')
    run(cmdline, check=True)
    output_dir = path('target/' + app_name + ('.app' if is_mac() else ''))
    rename(output_dir, path('${freeze_dir}'))