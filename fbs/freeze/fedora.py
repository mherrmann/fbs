from fbs.freeze.linux import freeze_linux, remove_shared_libraries

def freeze_fedora(debug=False):
    freeze_linux(debug)
    # Force Fedora to use the system's Gnome libraries. This avoids warnings
    # when starting the app on the command line.
    remove_shared_libraries('libgio-2.0.so.*', 'libglib-2.0.so.*')
    # Fixes for Fedora 29:
    remove_shared_libraries('libfreetype.so.*', 'libssl.so.*')
    # PyInstaller 3.4 includes the library below when on Python 3.6.
    # (Interestingly, it does not package it on Python 3.5.) This leads to a lot
    # of Fontconfig-related errors when starting the frozen app. Further,
    # starting the app takes ages. Removing the library fixes this:
    remove_shared_libraries('libfontconfig.so.*')