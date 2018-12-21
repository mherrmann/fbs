from fbs_runtime._settings import load_settings
from os import listdir
from os.path import join
from tempfile import TemporaryDirectory
from unittest import TestCase

import json

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