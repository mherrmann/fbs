from fbs_runtime import system
from fbs_runtime._signal import SignalWakeupHandler
from fbs_runtime.system import is_windows, is_mac
from functools import lru_cache
from os.path import join, exists, pardir, dirname, realpath
from pathlib import PurePath

try:
    from PyQt5.QtGui import QIcon
except ImportError:
    from PySide2.QtGui import QIcon
try:
    from PyQt5.QtWidgets import QApplication
except ImportError:
    from PySide2.QtWidgets import QApplication

import errno
import inspect
import os
import sys

def cached_property(getter):
    """
    A cached Python @property. You use it in conjunction with ApplicationContext
    below to instantiate the components that comprise your application. For more
    information, please consult the Manual:
        https://build-system.fman.io/manual/#cached_property
    """
    return property(lru_cache()(getter))

class ApplicationContext:
    """
    The main point of contact between your application and fbs. For information
    on how to use it, please see the Manual:
        https://build-system.fman.io/manual/#your-python-code
    """
    def __init__(self):
        self._resource_locator = self._create_resource_locator()
        # Many Qt classes require a QApplication to have been instantiated.
        # Do this here, before everything else, to achieve this:
        self.app
        # We don't build as a console app on Windows, so no point in installing
        # the SIGINT handler:
        if not is_windows():
            self._signal_wakeup_handler = SignalWakeupHandler(self.app)
            self._signal_wakeup_handler.install()
        if self.app_icon:
            self.app.setWindowIcon(self.app_icon)
    def _create_resource_locator(self):
        if is_frozen():
            executable_dir = dirname(sys.executable)
            if is_mac():
                resources_dir = join(executable_dir, pardir, 'Resources')
            else:
                resources_dir = executable_dir
            return _ResourceLocator([resources_dir])
        else:
            return _DevelopmentResourceLocator(self.__class__)
    @cached_property
    def app(self):
        """
        The global Qt QApplication object for your app. Feel free to overwrite
        this property, eg. if you wish to use your own subclass of QApplication.
        An example of this is given in the Manual.
        """
        return QApplication(sys.argv)
    @cached_property
    def app_icon(self):
        """
        The app icon. Not available on Mac because app icons are handled by the
        OS there.
        """
        if not is_mac():
            return QIcon(self.get_resource('Icon.ico'))
    def get_resource(self, *rel_path):
        """
        Return the absolute path to the data file with the given name or
        (relative) path. When running from source, searches src/main/resources.
        Otherwise, searches your app's installation directory. If no file with
        the given name or path exists, a FileNotFoundError is raised.
        """
        return self._resource_locator.locate(*rel_path)
    def run(self):
        raise NotImplementedError()

def is_frozen():
    """
    Return True if running from the frozen (i.e. compiled form) of your app, or
    False when running from source.
    """
    return getattr(sys, 'frozen', False)

@lru_cache()
def get_application_context(DevelopmentAppCtxtCls, FrozenAppCtxtCls=None):

    if FrozenAppCtxtCls is None:
        FrozenAppCtxtCls = DevelopmentAppCtxtCls
    return FrozenAppCtxtCls() if is_frozen() else DevelopmentAppCtxtCls()

class _ResourceLocator:
    def __init__(self, resource_dirs):
        self._dirs = resource_dirs
    def locate(self, *rel_path):
        for resource_dir in self._dirs:
            resource_path = join(resource_dir, *rel_path)
            if exists(resource_path):
                return realpath(resource_path)
        raise FileNotFoundError(
            errno.ENOENT, 'Could not locate resource', os.sep.join(rel_path)
        )

class _DevelopmentResourceLocator(_ResourceLocator):
    def __init__(self, appctxt_cls):
        project_dir = self._get_project_base_dir(appctxt_cls)
        resources_dir = join(project_dir, 'src', 'main', 'resources')
        resource_dirs = [
            join(resources_dir, system.name().lower()),
            join(resources_dir, 'base'),
            join(project_dir, 'src', 'main', 'icons')
        ]
        super().__init__(resource_dirs)
    def _get_project_base_dir(self, appctxt_cls):
        class_file = inspect.getfile(appctxt_cls)
        p = PurePath(class_file)
        while p != p.parent:
            parent_names = [p.parents[2].name, p.parents[1].name, p.parent.name]
            if parent_names == ['src', 'main', 'python']:
                return str(p.parents[3])
            p = p.parent
        raise RuntimeError(
            'Could not determine project base directory for %s. Is it in '
            'src/main/python?' % appctxt_cls
        )