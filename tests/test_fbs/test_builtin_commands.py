from fbs import path
from fbs.builtin_commands import freeze, installer
from fbs_runtime.platform import is_mac, is_windows, is_linux
from os import listdir
from os.path import exists, join
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
        if is_linux():
            applications_dir = path('target/installer/usr/share/applications')
            self.assertEqual(['MyApp.desktop'], listdir(applications_dir))
            with open(join(applications_dir, 'MyApp.desktop')) as f:
                self.assertIn('MyApp', f.read())
    def setUp(self):
        super().setUp()
        self.init_fbs()