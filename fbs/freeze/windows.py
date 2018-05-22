from fbs import path
from fbs.freeze import run_pyinstaller
from fbs.resources import generate_resources
from os import remove
from os.path import join, exists
from shutil import copy

import os
import struct
import sys

def freeze_windows(extra_pyinstaller_args=None):
    if extra_pyinstaller_args is None:
        extra_pyinstaller_args = []
    pyinstaller_args = [
        '--windowed',
        '--icon', path('src/main/icons/Icon.ico')
    ]
    run_pyinstaller(extra_args=pyinstaller_args + extra_pyinstaller_args)
    _restore_corrupted_python_dlls()
    generate_resources()
    copy(path('src/main/icons/Icon.ico'), path('${freeze_dir}'))
    _add_missing_dlls()

def _restore_corrupted_python_dlls():
    # PyInstaller somehow corrupts python3*.dll - see:
    # https://github.com/pyinstaller/pyinstaller/issues/2526
    # Restore the uncorrupted original:
    python_dlls = (
        'python%s.dll' % sys.version_info.major,
        'python%s%s.dll' % (sys.version_info.major, sys.version_info.minor)
    )
    for dll_name in python_dlls:
        try:
            remove(path('${freeze_dir}/' + dll_name))
        except FileNotFoundError:
            pass
        else:
            copy(_find_on_path(dll_name), path('${freeze_dir}'))

def _add_missing_dlls():
    for dll_name in (
        'msvcr100.dll', 'msvcr110.dll', 'msvcp110.dll', 'vcruntime140.dll',
        'msvcp140.dll', 'concrt140.dll', 'vccorlib140.dll'
    ):
        _add_missing_dll(dll_name)
    for ucrt_dll in ('api-ms-win-crt-multibyte-l1-1-0.dll',):
        try:
            _add_missing_dll(ucrt_dll)
        except LookupError:
            bitness_32_or_64 = struct.calcsize("P") * 8
            raise FileNotFoundError(
                "Could not find %s on your PATH. If you are on Windows 10, you "
                "may have to install the Windows 10 SDK from "
                "https://dev.windows.com/en-us/downloads/windows-10-sdk. "
                "Otherwise, try installing KB2999226 from "
                "https://support.microsoft.com/en-us/kb/2999226. "
                "In both cases, add the directory containing %s to your PATH "
                "environment variable afterwards. If there are 32 and 64 bit "
                "versions of the DLL, use the %s bit one (because that's the"
                "bitness of your current Python interpreter)." % (
                    ucrt_dll, ucrt_dll, bitness_32_or_64
                )
            ) from None

def _add_missing_dll(dll_name):
    freeze_dir = path('${freeze_dir}')
    if not exists(join(freeze_dir, dll_name)):
        copy(_find_on_path(dll_name), freeze_dir)

def _find_on_path(file_name):
    path = os.environ.get("PATH", os.defpath)
    path_items = path.split(os.pathsep)
    if sys.platform == "win32":
        if not os.curdir in path_items:
            path_items.insert(0, os.curdir)
    seen = set()
    for dir_ in path_items:
        normdir = os.path.normcase(dir_)
        if not normdir in seen:
            seen.add(normdir)
            file_path = join(dir_, file_name)
            if exists(file_path):
                return file_path
    raise LookupError("Could not find %s on PATH" % file_name)