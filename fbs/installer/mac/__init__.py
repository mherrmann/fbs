from fbs import path, SETTINGS
from os.path import join, dirname
from subprocess import run

def create_installer_mac():
    app_name = SETTINGS['app_name']
    run([
        join(dirname(__file__), 'yoursway-create-dmg', 'create-dmg'),
        '--volname', app_name,
        '--app-drop-link', '170', '10',
        '--icon', app_name + '.app', '0', '10',
        path('target/${app_name}.dmg'),
        path('${freeze_dir}')
    ], check=True)