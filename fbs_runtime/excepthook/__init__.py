"""
By default, fbs overwrites sys.excepthook for better error reporting:

 1) Applications based on PyQt5 or PySide2 are missing some stack trace entries
    in their tracebacks (see add_missing_qt_frames(...) below). fbs makes sure
    they are displayed, for easier debugging.
 2) Python < 3.8 does not call sys.excepthook for non-main threads. fbs ensures
    that its own excepthook (and thus eg. the benefits of 1) above) does get
    called, so you see all errors.
 3) fbs lets you define multiple `ExceptionHandler`s - see below. This lets you
    report errors through several channels. Eg. on the console, or on a hosted
    error reporting system.

You can customise these mechanisms using the classes and functions in this
module, and by changing ApplicationContext#exception_handlers and
...#excepthook.
"""

from collections import namedtuple

import sys
import threading
import traceback

class ExceptionHandler:
    """
    Extend this class to implement your own exception handler(s). Then, add it
    to your ApplicationContext#exception_handlers.
    """
    def init(self):
        pass
    def handle(self, exc_type, exc_value, enriched_tb):
        """
        Return True from this method to prevent further ExceptionHandlers from
        being invoked for this exception.
        """
        raise NotImplementedError()

class StderrExceptionHandler(ExceptionHandler):
    """
    Print exceptions to stderr.
    """
    def handle(self, exc_type, exc_value, enriched_tb):
        # Normally, we'd like to use sys.__excepthook__ here. But it doesn't
        # work with our "fake" traceback (see add_missing_qt_frames(...)).
        # The following call avoids this yet produces the same result:
        traceback.print_exception(exc_type, exc_value, enriched_tb)

class _Excepthook:
    """
    fbs's excepthook. Forwards exceptions to the given handlers, until one of
    them returns True. Adds stack trace entries that are normally missing in
    PyQt5 / PySide2 applications (see add_missing_qt_frames(...)). Also ensures
    that, unlike in Python normally, it is called for exceptions in all threads.
    """
    def __init__(self, handlers):
        self._handlers = handlers
    def install(self):
        for handler in self._handlers:
            handler.init()
        sys.excepthook = self
        enable_excepthook_for_threads()
    def __call__(self, exc_type, exc_value, exc_tb):
        if not isinstance(exc_value, SystemExit):
            enriched_tb = add_missing_qt_frames(exc_tb) if exc_tb else exc_tb
            for handler in self._handlers:
                if handler.handle(exc_type, exc_value, enriched_tb):
                    break

def enable_excepthook_for_threads():
    """
    `sys.excepthook` isn't called for exceptions raised in non-main-threads.
    This workaround fixes this for instances of (non-subclasses of) Thread.
    See: http://bugs.python.org/issue1230540
    """
    init_original = threading.Thread.__init__

    def init(self, *args, **kwargs):
        init_original(self, *args, **kwargs)
        run_original = self.run

        def run_with_except_hook(*args2, **kwargs2):
            try:
                run_original(*args2, **kwargs2)
            except Exception:
                sys.excepthook(*sys.exc_info())

        self.run = run_with_except_hook

    threading.Thread.__init__ = init

def add_missing_qt_frames(tb):
    """
    Let f and h be Python functions and g be a function of Qt. If
        f() -> g() -> h()
    (where "->" means "calls"), and an exception occurs in h(), then the
    traceback does not contain f. This can make debugging very difficult.
    To fix this, this function creates a "fake" traceback that contains the
    missing entries.

    The code below can be used to reproduce the f() -> g() -> h() problem.
    It opens a window with a button. When you click it, an error occurs
    whose traceback does not include f().

    The problem described here is not specific to PyQt5 - It occurs for
    PySide2 as well. To see this, replace PyQt5 by PySide2 below.

        from PyQt5.QtWidgets import *
        from PyQt5.QtCore import Qt

        class Window(QWidget):
            def __init__(self):
                super().__init__()
                btn = QPushButton('Click me', self)
                btn.clicked.connect(self.f)
            def f(self, _):
                self.inputMethodQuery(Qt.ImAnchorPosition)
            def inputMethodQuery(self, query):
                if query == Qt.ImAnchorPosition:
                    # Make Qt call inputMethodQuery(ImCursorPosition).
                    # This is our "g()":
                    return super().inputMethodQuery(query) # "g()"
                self.h()
            def h(self):
                raise Exception()

        app = QApplication([])
        window = Window()
        window.show()
        app.exec_()
    """
    result = _fake_tb(tb.tb_frame, tb.tb_lasti, tb.tb_lineno, tb.tb_next)
    frame = tb.tb_frame.f_back
    while frame:
        result = _fake_tb(frame, frame.f_lasti, frame.f_lineno, result)
        frame = frame.f_back
    return result

_fake_tb = \
    namedtuple('fake_tb', ('tb_frame', 'tb_lasti', 'tb_lineno', 'tb_next'))