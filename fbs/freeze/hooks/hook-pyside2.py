"""
This hook is in particular required to prevent errors with the following code
under PySide2 5.12.1:

    from PySide2.QtWidgets import QApplication
    print(QApplication.__signature__)

It should print

    [<Signature (self)>, <Signature (self, arg__1:typing.List)>]

Without this hook, it prints a lot of output of the form

    parser.py:191: RuntimeWarning: pyside_type_init:
    UNRECOGNIZED: 'PySide2.QtGui....'

Then, it prints Signature('QStringList') instead of the above ...(List).
"""

from glob import glob
from os.path import dirname, relpath, join

import PySide2.support

"""
This should give roughly the same results as:
 
    from PyInstaller.utils.hooks import collect_data_files
    datas = collect_data_files(
        'PySide2', include_py_files=True, subdir='support'
    )

The reason we don't do it this way is that it would add a dynamic link to
PyInstaller, and thus force the GPL on fbs, preventing it from being licensed
under different terms (such as a commercial license).
"""
_base_dir = dirname(PySide2.support.__file__)
_python_files = glob(join(_base_dir, '**', '*.py'), recursive=True)
_site_packages = dirname(dirname(_base_dir))
datas = [(f, relpath(dirname(f), _site_packages)) for f in _python_files]