from socket import socketpair, SOCK_DGRAM

import signal

class SignalWakeupHandler:
    """
    Python's `signal` module lets us define custom signal handlers. What we want
    in particular is a graceful handling of Ctrl+C, meaning that the app shuts
    down cleanly.

    The default implementation in Python (ie. if we don't set any signals) is to
    raise KeyboardInterrupt at arbitrary points in our code. This is not nice or
    easy to handle.

    The simplest implementation would be to call `signal(SIGINT, SIG_DFL)`. This
    immediately kills the app when the user presses Ctrl in the console window
    attached to it. This is not nice because no shutdown/cleanup code is
    executed.

    Another implementation would be to call `signal(SIGINT, ...app.exit())`. The
    problem is: This signal seems to only be delivered when the app has focus.
    So the user presses Ctrl+C in the console, then needs to switch to the GUI
    window for the signal to be delivered and the app to shut down. Not nice
    either.

    The present class fixes this problem. It integrates Python and Qt so that
    signal handlers installed with Python get called immediately. This way, we
    can immediately quit the app when the user presses Ctrl+C in the console.

    See: https://stackoverflow.com/a/37229299/1839209
    """
    def __init__(self, app, QAbstractSocket):
        self._app = app
        self.old_fd = None
        # Create a socket pair
        self.wsock, self.rsock = socketpair(type=SOCK_DGRAM)
        self.socket = QAbstractSocket(QAbstractSocket.UdpSocket, app)
        # Let Qt listen on the one end
        self.socket.setSocketDescriptor(self.rsock.fileno())
        # And let Python write on the other end
        self.wsock.setblocking(False)
        self.old_fd = signal.set_wakeup_fd(self.wsock.fileno())
        # First Python code executed gets any exception from
        # the signal handler, so add a dummy handler first
        self.socket.readyRead.connect(lambda : None)
        # Second handler does the real handling
        self.socket.readyRead.connect(self._readSignal)
    def install(self):
        signal.signal(signal.SIGINT, lambda *_: self._app.exit(130))
    def __del__(self):
        # Restore any old handler on deletion
        if self.old_fd is not None and signal and signal.set_wakeup_fd:
            signal.set_wakeup_fd(self.old_fd)
    def _readSignal(self):
        # Read the written byte.
        # Note: readyRead is blocked from occurring again until readData()
        # was called, so call it, even if you don't need the value.
        _ = self.socket.readData(1)