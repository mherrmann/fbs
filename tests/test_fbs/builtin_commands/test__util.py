from fbs.builtin_commands._util import _update_json_str
from unittest import TestCase

class UpdateJsonStrTest(TestCase):
    def test_empty(self):
        json_str = '{\n\t"a": "b"}'
        self.assertEqual(json_str, _update_json_str(json_str, {}))
    def test_single(self):
        json_str = '{\n\t"a": "b"}'
        self.assertEqual(
            '{\n\t"a": "b",\n\t"c": "d"\n}',
            _update_json_str(json_str, {'c': 'd'})
        )
    def test_spaces(self):
        self.assertEqual(
            '{\n    "a": "b",\n    "c": "d"\n}',
            _update_json_str('{\n    "a": "b"}', {'c': 'd'})
        )