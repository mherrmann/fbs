from fbs import path
from fbs.resources import generate_resources
from os.path import exists
from tests.test_fbs import FbsTest

class GenerateResourcesTest(FbsTest):
    def test_generate_resources(self):
        generate_resources()
        self.assertTrue(exists(path('${freeze_dir}/Contents/Info.plist')))