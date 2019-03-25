from glob import glob
from os.path import dirname, relpath, join

import PySide2

if PySide2.__version__ == "5.12.2":
    import PySide2.support as support
else:
    import shiboken2.support as support

"""
This should give roughly the same results as:

    from PyInstaller.utils.hooks import collect_data_files
    datas = collect_data_files(
        'shiboken2', include_py_files=True, subdir='support'
    )

The reason we don't do it this way is that it would add a dynamic link to
PyInstaller, and thus force the GPL on fbs, preventing it from being licensed
under different terms (such as a commercial license).
"""
_base_dir = dirname(support.__file__)
_python_files = glob(join(_base_dir, '**', '*.py'), recursive=True)
_site_packages = dirname(dirname(_base_dir))
datas = [(f, relpath(dirname(f), _site_packages)) for f in _python_files]

hiddenimports = ['typing']
