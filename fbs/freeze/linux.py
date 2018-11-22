from fbs import path
from fbs.freeze import _generate_resources, run_pyinstaller
from glob import glob
from os import remove
from shutil import copy

def freeze_linux(debug=False):
    run_pyinstaller(debug=debug)
    _generate_resources()
    copy(path('src/main/icons/Icon.ico'), path('${freeze_dir}'))
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
        for file_path in glob(path('${freeze_dir}/' + pattern)):
            remove(file_path)