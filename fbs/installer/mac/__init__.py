import platform
from fbs import path, SETTINGS
from fbs_runtime.platform import is_mac
from os import replace, remove
from os.path import join, dirname, exists
from subprocess import check_call, DEVNULL


def create_installer_mac():
    app_name = SETTINGS['app_name']
    dest = path('target/${installer}')
    dest_existed = exists(dest)
    if dest_existed:
        dest_bu = dest + '.bu'
        replace(dest, dest_bu)
    try:
        pdata = [
            join(dirname(__file__), 'create-dmg', 'create-dmg'),
            '--volname', app_name,
            '--app-drop-link', '170', '10',
            '--icon', app_name + '.app', '0', '10',
            dest,
            path('${freeze_dir}')
        ]

        if is_mac():
            major, minor = platform.mac_ver()[0].split('.')[:2]
            if (int(major) == 10 and int(minor) >= 15) or int(major) >= 11:
                pdata.insert(1, '--no-internet-enable')

        check_call(pdata, stdout=DEVNULL)
    except:
        if dest_existed:
            replace(dest_bu, dest)
        raise
    else:
        if dest_existed:
            remove(dest_bu)
