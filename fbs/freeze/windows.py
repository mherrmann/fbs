from fbs import path, SETTINGS
from fbs.freeze import run_pyinstaller, _generate_resources
from fbs.resources import _copy
from fbs_runtime._source import default_path
from os import remove
from os.path import join, exists
from shutil import copy

import os
import struct
import sys

def freeze_windows(debug=False):
    args = []
    if not (debug or SETTINGS['show_console_window']):
        # The --windowed flag below prevents us from seeing any console output.
        # We therefore only add it when we're not debugging.
        args.append('--windowed')
    args.extend(['--icon', path('src/main/icons/Icon.ico')])
    for path_fn in default_path, path:
        _copy(path_fn, 'src/freeze/windows/version_info.py', path('target/PyInstaller'))
    args.extend(['--version-file', path('target/PyInstaller/version_info.py')])
    run_pyinstaller(args, debug)
    _restore_corrupted_python_dlls()
    _generate_resources()
    copy(path('src/main/icons/Icon.ico'), path('${freeze_dir}'))
    _add_missing_dlls()

def _restore_corrupted_python_dlls():
    # PyInstaller <= 3.4 somehow corrupts python3*.dll - see:
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
        try:
            _add_missing_dll(dll_name)
        except LookupError:
            raise FileNotFoundError(
                "Could not find %s on your PATH. Please install the Visual C++ "
                "Redistributable for Visual Studio 2012 from:\n    "
                "https://www.microsoft.com/en-us/download/details.aspx?id=30679"
                % dll_name
            ) from None
    for ucrt_dll in ('api-ms-win-crt-multibyte-l1-1-0.dll',):
        try:
            _add_missing_dll(ucrt_dll)
        except LookupError:
            bitness_32_or_64 = struct.calcsize("P") * 8
            raise FileNotFoundError(
                "Could not find %s on your PATH. If you are on Windows 10, you "
                "may have to install the Windows 10 SDK from "
                "https://developer.microsoft.com/en-us/windows/downloads/windows-10-sdk. "
                "Otherwise, try installing KB2999226 from "
                "https://support.microsoft.com/en-us/kb/2999226. "
                "In both cases, add the directory containing %s to your PATH "
                "environment variable afterwards. If there are 32 and 64 bit "
                "versions of the DLL, use the %s bit one (because that's the "
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
