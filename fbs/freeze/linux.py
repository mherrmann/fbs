from fbs.conf import path
from fbs.freeze import run_pyinstaller
from fbs.resources import generate_resources
from glob import glob
from os import remove
from shutil import copy

def freeze_linux():
	run_pyinstaller()
	generate_resources(dest_dir=path('target/app'))
	copy(path('src/main/icons/Icon.ico'), path('target/app'))
	# For some reason, PyInstaller packages libstdc++.so.6 even though it is
	# available on most Linux distributions. If we include it and run our app on
	# a different Ubuntu version, then Popen(...) calls fail with errors
	# "GLIBCXX_... not found" or "CXXABI_..." not found. So ensure we don't
	# package the file, so that the respective system's compatible version is
	# used:
	remove_shared_libraries(
		'libstdc++.so.*', 'libtinfo.so.*', 'libreadline.so.*', 'libdrm.so.*'
	)

def remove_shared_libraries(*filename_patterns):
	for pattern in filename_patterns:
		for file_path in glob(path('target/app/' + pattern)):
			remove(file_path)