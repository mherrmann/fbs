from fbs_runtime.licensing import pack_license_key, unpack_license_key, \
    InvalidKey
from unittest import TestCase

import json

class LicensingTest(TestCase):
    def test_generate_then_load_license_key(self):
        keydata = pack_license_key(self._data, self._privkey)
        self.assertEqual(self._data, unpack_license_key(keydata, self._pubkey))
    def test_empty_key(self):
        self._check_invalid_key('')
    def test_no_signature(self):
        self._check_invalid_key(json.dumps(self._data))
    def test_user_tampered_with_key(self):
        keydata_str = pack_license_key(self._data, self._privkey)
        keydata = json.loads(keydata_str)
        keydata['date'] = '2020-01-02'
        keydata_modified = json.dumps(keydata)
        self._check_invalid_key(keydata_modified)
    def _check_invalid_key(self, keydata):
        with self.assertRaises(InvalidKey):
            unpack_license_key(keydata, self._pubkey)
    def setUp(self):
        super().setUp()
        self._privkey = {
            'n': 9116365493586701555158688922318831122873224915843805750251776548409677052914547431708264536351375628651794208119141013931263465930598754883605782199184293,
            'e': 65537,
            'd': 6266571028366890536031538458435133467895063589403900835388292621051557912362806486944414077848185078422091551985740742061462958257856016077331527399436673,
            'p': 7353587414156093503501011792798870181671531836014338388885442376689613159376021937,
            'q': 1239716750498832082588803847923980076640962859612412544106088598157748789
        }
        self._pubkey = {
            'n': 9116365493586701555158688922318831122873224915843805750251776548409677052914547431708264536351375628651794208119141013931263465930598754883605782199184293,
            'e': 65537
        }
        self._data = {'email': 'some@user.com', 'date': '2019-01-02'}