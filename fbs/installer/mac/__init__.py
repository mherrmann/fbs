from fbs import path, SETTINGS
from os import replace, remove
from os.path import join, dirname, exists
from subprocess import run

def create_installer_mac():
    app_name = SETTINGS['app_name']
    dest = path('target/${installer}')
    dest_existed = exists(dest)
    if dest_existed:
        dest_bu = dest + '.bu'
        replace(dest, dest_bu)
    try:
        run([
            join(dirname(__file__), 'yoursway-create-dmg', 'create-dmg'),
            '--volname', app_name,
            '--app-drop-link', '170', '10',
            '--icon', app_name + '.app', '0', '10',
            dest,
            path('${freeze_dir}')
        ], check=True)
    except:
        if dest_existed:
            replace(dest_bu, dest)
        raise
    else:
        if dest_existed:
            remove(dest_bu)