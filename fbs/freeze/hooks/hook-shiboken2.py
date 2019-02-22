from glob import glob
from os.path import dirname, relpath, join

import shiboken2.support

_base_dir = dirname(shiboken2.support.__file__)
_python_files = glob(join(_base_dir, '**', '*.py'), recursive=True)
_site_packages = dirname(dirname(_base_dir))
datas = [(f, relpath(dirname(f), _site_packages)) for f in _python_files]

hiddenimports = ['typing']