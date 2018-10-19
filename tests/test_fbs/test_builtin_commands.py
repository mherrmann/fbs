from fbs import path
from fbs.builtin_commands import freeze, installer
from fbs_runtime.platform import is_mac, is_windows
from os.path import exists
from tests.test_fbs import FbsTest

class BuiltInCommandsTest(FbsTest):
    def test_freeze_installer(self):
        freeze()
        if is_mac():
            executable = path('${freeze_dir}/Contents/MacOS/${app_name}')
        elif is_windows():
            executable = path('${freeze_dir}/${app_name}.exe')
        else:
            executable = path('${freeze_dir}/${app_name}')
        self.assertTrue(exists(executable), executable + ' does not exist')
        installer()
        self.assertTrue(exists(path('target/${installer}')))
    def setUp(self):
        super().setUp()
        self.init_fbs()