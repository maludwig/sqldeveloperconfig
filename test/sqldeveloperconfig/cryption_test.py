import unittest

from sqldeveloperconfig.cryption import encrypt_v4, decrypt_v4
from test.sqldeveloperconfig.test_constants import PLAINTEXT_PASSWORD, ENCRYPTED_PASSWORD, DB_SYSTEM_ID


class TestCryption(unittest.TestCase):
    def test_crypting_v4(self):
        encrypted_password = encrypt_v4(PLAINTEXT_PASSWORD, DB_SYSTEM_ID)
        self.assertEqual(encrypted_password, ENCRYPTED_PASSWORD)
        plaintext_password = decrypt_v4(encrypted_password, DB_SYSTEM_ID)
        self.assertEqual(plaintext_password, PLAINTEXT_PASSWORD)

        encrypted_password = encrypt_v4("", DB_SYSTEM_ID)
        self.assertEqual(encrypted_password, "")
        plaintext_password = decrypt_v4("", DB_SYSTEM_ID)
        self.assertEqual(plaintext_password, "")


if __name__ == "__main__":
    unittest.main()
