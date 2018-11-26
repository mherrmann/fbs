from fbs.freeze.linux import freeze_linux, remove_shared_libraries

def freeze_ubuntu(debug=False):
    freeze_linux(debug)
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
    # libgtk-3.so is present on every Ubuntu system. Make sure we don't ship it
    # to avoid incompatibilities. In particular, running the frozen app with
    # libgtk-3.so from Ubuntu 14 on Ubuntu 16 produces many Gtk warnings
    # "Theme parsing error".
    remove_shared_libraries('libgtk-3.so.*')
    # We also don't want to ship libgio-2.0.so because it is usually present.
    # What's more, if we ship libgio without libgtk, then segmentation faults
    # occur when freezing on Ubuntu 14 and running on Ubuntu 16. The reason for
    # this is that libgio depends on libgtk. Because we don't ship libgtk, this
    # loads the user's libgtk, which is incompatible between Ubuntu 14 and 16.
    remove_shared_libraries('libgio-2.0.so.*')