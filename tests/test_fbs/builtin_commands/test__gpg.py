from fbs.builtin_commands._gpg import _extend_json
from unittest import TestCase

class ExtendJsonTest(TestCase):
    def test_empty(self):
        json_str = '{\n\t"a": "b"}'
        self.assertEqual(json_str, _extend_json(json_str, {}))
    def test_single(self):
        json_str = '{\n\t"a": "b"}'
        self.assertEqual(
            '{\n\t"a": "b",\n\t"c": "d"\n}', _extend_json(json_str, {'c': 'd'})
        )
    def test_spaces(self):
        self.assertEqual(
            '{\n    "a": "b",\n    "c": "d"\n}',
            _extend_json('{\n    "a": "b"}', {'c': 'd'})
        )