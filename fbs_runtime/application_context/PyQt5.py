"""
Earlier fbs versions had the following code:

    try:
        from PyQt5 import ...
    except ImportError:
        from PySide2 import ...

This lead to problems when both PyQt5 and PySide2 were on PYTHONPATH:

 1) PyInstaller packaged both (!) libraries because it saw both imports.
 2) The above made fbs always use PyQt5. But if the user's app uses PySide2,
    then PySide2 and PyQt5 classes / code would be mixed.
 3) It wasn't clear (or deterministic, really) which Python binding took
    precedence. For instance, PyQt5 and PySide2 set different QML search paths.

To fix this problems, the above code was split into separate files: One that
contains all PyQt5 imports, and another that contains all PySide2 imports. The
user is supposed to import precisely one of the two. This makes PyInstaller
only package the one necessary library, and prevents the above problems.
"""

from . import _ApplicationContext, _QtBinding, cached_property
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from PyQt5.QtNetwork import QAbstractSocket

class ApplicationContext(_ApplicationContext):
    @cached_property
    def _qt_binding(self):
        return _QtBinding(QApplication, QIcon, QAbstractSocket)