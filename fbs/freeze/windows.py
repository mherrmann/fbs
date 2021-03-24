from fbs import path, SETTINGS
from fbs.freeze import run_pyinstaller, _generate_resources
from os import remove
from os.path import join, exists
from shutil import copy

import os
import struct
import sys

def create_version_file_windows(company=None):
    if company is None:
        company = SETTINGS['author']

    file_version_info = f"""# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx

VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0. Must always contain 4 elements.
    filevers=({SETTINGS['version'].replace('.', ',')},0),
    prodvers=({SETTINGS['version'].replace('.', ',')},0),
    # Contains a bitmask that specifies the valid bits 'flags'r
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x40004,
    # The general type of file.
    # 0x1 - the file is an application.
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'{company}'),
        StringStruct(u'FileDescription', u'{SETTINGS['app_name']}'),
        StringStruct(u'FileVersion', u'{SETTINGS['version']}.0'),
        StringStruct(u'InternalName', u'{SETTINGS['app_name']}'),
        StringStruct(u'LegalCopyright', u'© {SETTINGS['author']}. All rights reserved.'),
        StringStruct(u'OriginalFilename', u'{SETTINGS['app_name']}.exe'),
        StringStruct(u'ProductName', u'{SETTINGS['app_name']}'),
        StringStruct(u'ProductVersion', u'{SETTINGS['version']}.0')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)"""

    with open("file_version_info.txt", "w", encoding='utf-8') as outfile:
        outfile.write(file_version_info)


def freeze_windows(debug=False):
    args = []
    if not (debug or SETTINGS['show_console_window']):
        # The --windowed flag below prevents us from seeing any console output.
        # We therefore only add it when we're not debugging.
        args.append('--windowed')
    args.extend(['--icon', path('src/main/icons/Icon.ico')])
    create_version_file_windows()
    # If Version file exists in repo root we want to make sure PyInstaller is passed it as an argument:
    # https://pyinstaller.readthedocs.io/en/stable/usage.html#capturing-windows-version-data
    file = path('file_version_info.txt')
    # if file.exists():
    #     args.extend(['--version-file', path('file_version_info.txt')])
    args.extend(['--version-file', path('file_version_info.txt')])
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
