from os.path import join, dirname
from shutil import copytree
from tempfile import TemporaryDirectory
from unittest import TestCase

import fbs
import fbs.builtin_commands
import fbs._state as fbs_state
import fbs_runtime._state as runtime_state

class FbsTest(TestCase):
    def setUp(self):
        super().setUp()
        # Copy template project to temporary directory:
        self._tmp_dir = TemporaryDirectory()
        self._project_dir = join(self._tmp_dir.name, 'project')
        project_template = \
            join(dirname(fbs.builtin_commands.__file__), 'project_template')
        copytree(project_template, self._project_dir)
        # Save fbs's state:
        self._fbs_state_before = fbs_state.get()
        self._runtime_state_before = runtime_state.get()
        # Init fbs as if we were on Mac:
        runtime_state.restore('Mac', None, None)
        fbs.init(self._project_dir)
    def tearDown(self):
        runtime_state.restore(*self._runtime_state_before)
        fbs_state.restore(*self._fbs_state_before)
        self._tmp_dir.cleanup()
        super().tearDown()