import unittest
from orders import normalize_account


class AccountTest(unittest.TestCase):
    def test_normalizes(self):
        self.assertEqual(normalize_account(" ALPHA "), "alpha")
