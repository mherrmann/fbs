from fbs import path, SETTINGS
from fbs.resources import copy_with_filtering
from subprocess import run

def create_installer_windows():
	installer_nsi = path('src/main/Installer.nsi')
	copy_with_filtering(
		installer_nsi,
		path('target/NSIS'),
		replacements={
			'app_name': SETTINGS['app_name'],
			'author': SETTINGS['author']
		},
		files_to_filter=[installer_nsi],
		placeholder='%%{%s}'
	)
	try:
		run(['makensis', 'Installer.nsi'], cwd=path('target/NSIS'), check=True)
	except FileNotFoundError:
		raise FileNotFoundError(
			"fbs could not find executable 'makensis'. Please install NSIS and "
			"add its installation directory to your PATH environment variable."
		) from None