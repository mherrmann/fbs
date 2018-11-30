from fbs import load_settings, SETTINGS
from os import listdir
from os.path import join
from tempfile import TemporaryDirectory
from tests.test_fbs import FbsTest
from unittest import TestCase

import json

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

class LoadSettingsTest(TestCase):
    def test_empty(self):
        self._check({})
    def test_string(self):
        self._check({'key': 'value'})
    def test_int(self):
        self._check({'key': 2})
    def test_multiple(self):
        self._check(
            {'a': 'b'}, {'c': 'd'},
            expect={'a': 'b', 'c': 'd'}
        )
    def test_replace(self):
        self._check(
            {
                'app_name': 'MyApp',
                'freeze_dir': 'target/${app_name}'
            },
            expect={
                'app_name': 'MyApp',
                'freeze_dir': 'target/MyApp'
            }
        )
    def test_replace_across_files(self):
        self._check(
            {'app_name': 'MyApp'}, {'freeze_dir': 'target/${app_name}'},
            expect={'app_name': 'MyApp', 'freeze_dir': 'target/MyApp'}
        )
    def test_list(self):
        self._check({'list': ['item 1', 'item 2']})
    def test_merge_lists(self):
        self._check(
            {'list': ['a']}, {'list': ['b']},
            expect={'list': ['a', 'b']}
        )
    def test_replace_in_list(self):
        self._check(
            {'l': ['${a}'], 'a': 'b'},
            expect={'l': ['b'], 'a': 'b'}
        )
    def test_replace_in_dict(self):
        self._check(
            {'d': {'x': '${a}'}, 'a': 'b'},
            expect={'d': {'x': 'b'}, 'a': 'b'}
        )
    def test_existing(self):
        # fbs.init(...) sets the `project_dir` setting. Test that this setting
        # is available to further settings in .json files:
        existing = {'project_dir': '/myproject'}
        fedora_json = self._dump({
            'repo_url': 'file://${project_dir}/target/repo'
        })
        expected = {
            'repo_url': 'file:///myproject/target/repo',
            'project_dir': '/myproject'
        }
        self.assertEqual(expected, load_settings([fedora_json], existing))
    def _check(self, *objs, expect=None):
        if expect is None:
            expect, = objs
        files = [self._dump(o) for o in objs]
        self.assertEqual(expect, load_settings(files))
    def _dump(self, data):
        fname = str(len(listdir(self._tmp_dir.name)))
        fpath = join(self._tmp_dir.name, fname)
        with open(fpath, 'x') as f:
            json.dump(data, f)
        return fpath
    def setUp(self):
        super().setUp()
        self._tmp_dir = TemporaryDirectory()
    def tearDown(self):
        self._tmp_dir.cleanup()
        super().tearDown()