from fbs.freeze.linux import freeze_linux, remove_shared_libraries

def freeze_arch(extra_pyinstaller_args=None):
    freeze_linux(extra_pyinstaller_args)
    # Our apps normally ship with eg. libQt5Core.so.5. This loads other .so
    # files, if present, from /usr/lib. If those libraries are Qt libraries of a
    # different Qt version, errors occur.
    # For this reason, on systems with pacman, we don't include Qt. Instead, we
    # declare it as a dependency and leave it up to pacman to fetch it.
    remove_shared_libraries('libicudata.so.*', 'libQt*.so.*')