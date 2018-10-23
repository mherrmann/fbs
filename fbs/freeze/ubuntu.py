from fbs.freeze.linux import freeze_linux, remove_shared_libraries

def freeze_ubuntu(extra_pyinstaller_args=None, debug=False):
    freeze_linux(extra_pyinstaller_args, debug)
    # When we build on Ubuntu on 14.04 and run on 17.10, the app fails to start
    # with the following error:
    #
    #  > This application failed to start because it could not find or load the
    #  > Qt platform plugin "xcb" in "". Available platform plugins are:
    #  > eglfs, linuxfb, minimal, minimalegl, offscreen, vnc, xcb.
    #
    # Interestingly, the error does not occur when building on Ubuntu 16.04.
    # The difference between the two build outputs seems to be
    # libgpg-error.so.0. Removing it fixes the problem:
    remove_shared_libraries('libgpg-error.so.*')