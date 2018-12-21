from fbs import SETTINGS
from tests.test_fbs import FbsTest

class LinuxSettingsTest(FbsTest):
    def test_default_does_not_overwrite(self):
        # Consider the following scenario: The user sets "url" in base.json
        # instead of the usual linux.json. If we loaded settings in the
        # following order:
        #  1) default base
        #  2) user base
        #  3) default linux
        #  4) user linux
        # Then 3) would overwrite 2) and thus the user's "url" setting.
        # This test ensures that the load order is instead:
        #  1) default base
        #  2) default linux
        #  3) user base
        #  4) user linux.
        self._update_settings('base.json', {'url': 'build-system.fman.io'})

        # The project template's linux.json sets url="". This defeats the
        # purpose of this test. So delete the setting:
        linux_settings = self._read_settings('linux.json')
        del linux_settings['url']
        self._write_settings('linux.json', linux_settings)

        self.init_fbs('Linux')
        self.assertEqual('build-system.fman.io', SETTINGS['url'])