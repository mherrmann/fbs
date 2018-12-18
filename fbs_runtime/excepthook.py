from collections import namedtuple

import sys
import threading
import traceback

class Excepthook:
    def install(self):
        sys.excepthook = self
        self._enable_excepthook_for_threads()
    def __call__(self, exc_type, exc_value, exc_tb):
        if not isinstance(exc_value, SystemExit):
            enriched_tb = self._add_missing_frames(exc_tb) if exc_tb else exc_tb
            # Normally, we'd like to use sys.__excepthook__ here. But it doesn't
            # work with our "fake" traceback (see #_add_missing_frames(...)).
            # The following call avoids this yet produces the same result:
            traceback.print_exception(exc_type, exc_value, enriched_tb)
    def _add_missing_frames(self, tb):
        """
        Let f and h be Python functions and g be a function of Qt. If
            f() -> g() -> h()
        (where "->" means "calls"), and an exception occurs in h(), then the
        traceback does not contain f. This can make debugging very difficult.
        To fix this, we create a "fake" traceback that contains the missing
        entries.

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
    def _enable_excepthook_for_threads(self):
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

_fake_tb = \
    namedtuple('fake_tb', ('tb_frame', 'tb_lasti', 'tb_lineno', 'tb_next'))