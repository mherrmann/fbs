from fbs import path
from fbs.freeze import _generate_resources
from os.path import exists
from tests.test_fbs import FbsTest

class GenerateResourcesTest(FbsTest):
    def test_generate_resources(self):
        self.init_fbs('Mac')
        _generate_resources()
        info_plist = path('${freeze_dir}/Contents/Info.plist')
        self.assertTrue(exists(info_plist))
        with open(info_plist) as f:
            self.assertIn(
                'MyApp', f.read(), "Did not replace '${app_name}' by 'MyApp'"
            )