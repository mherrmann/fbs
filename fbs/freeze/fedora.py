from fbs.freeze.linux import freeze_linux, remove_shared_libraries

def freeze_fedora(extra_pyinstaller_args=None, debug=False):
    freeze_linux(extra_pyinstaller_args, debug)
    # Force Fedora to use the system's Gnome libraries. This avoids warnings
    # when starting the app on the command line.
    remove_shared_libraries('libgio-2.0.so.*', 'libglib-2.0.so.*')
    # Fix for Fedora 29:
    remove_shared_libraries('libfreetype.so.*')