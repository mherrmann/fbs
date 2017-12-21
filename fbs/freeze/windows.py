from fbs.conf import path
from fbs.freeze import run_pyinstaller
from fbs.resources import generate_resources
from os import remove
from os.path import join, dirname
from shutil import copy

import sys

def freeze_windows(extra_pyinstaller_args=None):
	if extra_pyinstaller_args is None:
		extra_pyinstaller_args = []
	args = [
		'--windowed',
		'--icon', path('src/main/icons/Icon.ico')
	] + extra_pyinstaller_args
	run_pyinstaller(extra_args=args)
	# PyInstaller somehow corrupts python3*.dll - see:
	# https://github.com/pyinstaller/pyinstaller/issues/2526
	# Restore the uncorrupted original:
	for dll_name in ('python3.dll', 'python35.dll'):
		remove(path('${freeze_dir}/' + dll_name))
		copy(join(dirname(sys.executable), dll_name), path('${freeze_dir}'))
	generate_resources(dest_dir=path('${freeze_dir}'))
	copy(path('src/main/icons/Icon.ico'), path('${freeze_dir}'))
	_add_missing_dlls()

def _add_missing_dlls():
	for dll in (
		'msvcr100.dll', 'msvcr110.dll', 'msvcp110.dll', 'vcruntime140.dll',
		'msvcp140.dll', 'concrt140.dll', 'vccorlib140.dll',
		'api-ms-win-crt-multibyte-l1-1-0.dll'
	):
		copy(join(r'c:\Windows\System32', dll), path('${freeze_dir}'))