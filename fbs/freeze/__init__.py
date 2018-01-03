from fbs import path, SETTINGS
from fbs.platform import is_mac
from os import rename
from subprocess import run

def run_pyinstaller(extra_args=None):
    if extra_args is None:
        extra_args = []
    app_name = SETTINGS['app_name']
    cmdline = [
        'pyinstaller',
        '--name', app_name,
        '--noupx',
        '--log-level', 'WARN'
    ] + extra_args + [
        '--distpath', path('target'),
        '--specpath', path('target/PyInstaller'),
        '--workpath', path('target/PyInstaller'),
        SETTINGS['main_module']
    ]
    run(cmdline, check=True)
    output_dir = path('target/' + app_name + ('.app' if is_mac() else ''))
    rename(output_dir, path('${freeze_dir}'))