'''
Test permission.
'''

from django.test import TestCase

from apps.user.permissions import encode
from apps.user.permissions import encode_maili
from apps.user.permissions import valid


class TestPermission(TestCase):
    def test_encode(self):
        msg = '18857453090'
        secret = encode(msg)
        self.assertIsNotNone(secret)
        
    def test_encode_maili(self):
        encode = encode_maili()
        self.assertIsNotNone(encode)
        self.assertEqual(encode, 32)
        
    def test_valid(self):
        key = encode_maili()
        okay = valid(key)
        self.assertTrue(okay)

        okay = valid('wrong-key')
        self.assertFalse(okay)
