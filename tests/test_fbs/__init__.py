from fbs.resources import copy_with_filtering
from os.path import join, dirname
from tempfile import TemporaryDirectory
from unittest import TestCase

import fbs
import fbs.builtin_commands
import fbs._state as fbs_state
import fbs_runtime._state as runtime_state
import json

class FbsTest(TestCase):
    def setUp(self):
        super().setUp()
        # Copy template project to temporary directory:
        self._tmp_dir = TemporaryDirectory()
        self._project_dir = join(self._tmp_dir.name, 'project')
        project_template = \
            join(dirname(fbs.builtin_commands.__file__), 'project_template')
        replacements = { 'python_bindings': 'PyQt5' }
        filter_ = [join(project_template, 'src', 'main', 'python', 'main.py')]
        copy_with_filtering(
            project_template, self._project_dir, replacements, filter_
        )
        self._update_settings('base.json', {'app_name': 'MyApp'})
        # Save fbs's state:
        self._fbs_state_before = fbs_state.get()
        self._runtime_state_before = runtime_state.get()
    def init_fbs(self, platform_name=None):
        if platform_name is not None:
            runtime_state.restore(platform_name, None, None)
        fbs.init(self._project_dir)
    def tearDown(self):
        runtime_state.restore(*self._runtime_state_before)
        fbs_state.restore(*self._fbs_state_before)
        self._tmp_dir.cleanup()
        super().tearDown()
    def _update_settings(self, json_name, dict_):
        settings = self._read_settings(json_name)
        settings.update(dict_)
        self._write_settings(json_name, settings)
    def _read_settings(self, json_name):
        with open(self._json_path(json_name)) as f:
            return json.load(f)
    def _write_settings(self, json_name, dict_):
        with open(self._json_path(json_name), 'w') as f:
            json.dump(dict_, f)
    def _json_path(self, name):
        return join(self._project_dir, 'src', 'build', 'settings', name)