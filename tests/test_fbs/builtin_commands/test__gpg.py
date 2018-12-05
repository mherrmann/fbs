from fbs.builtin_commands._gpg import _extend_json_str
from unittest import TestCase

class ExtendJsonStrTest(TestCase):
    def test_empty(self):
        json_str = '{\n\t"a": "b"}'
        self.assertEqual(json_str, _extend_json_str(json_str, {}))
    def test_single(self):
        json_str = '{\n\t"a": "b"}'
        self.assertEqual(
            '{\n\t"a": "b",\n\t"c": "d"\n}',
            _extend_json_str(json_str, {'c': 'd'})
        )
    def test_spaces(self):
        self.assertEqual(
            '{\n    "a": "b",\n    "c": "d"\n}',
            _extend_json_str('{\n    "a": "b"}', {'c': 'd'})
        )