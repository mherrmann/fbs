from fbs import path, SETTINGS
from fbs.resources import copy_with_filtering
from os.path import join, dirname
from subprocess import run

def create_installer_windows():
	setup_nsi = join(dirname(__file__), 'Setup.nsi')
	copy_with_filtering(
		setup_nsi,
		path('target/NSIS'),
		replacements={
			'app_name': SETTINGS['app_name'],
			'author': SETTINGS['author']
		},
		files_to_filter=[setup_nsi],
		placeholder='%%{%s}'
	)
	try:
		run(['makensis', 'Setup.nsi'], cwd=path('target/NSIS'), check=True)
	except FileNotFoundError:
		raise FileNotFoundError(
			"fbs could not find executable 'makensis'. Please install NSIS and "
			"add its installation directory to your PATH environment variable."
		) from None